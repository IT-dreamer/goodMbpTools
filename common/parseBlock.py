import sys
import io
import json
from simulinkmodel import parse as blxmlParse

# verbose レベル
verbose = 0

# 最初のSubSystem
first_subsystem = True

class ElementBase:
    """BLXMLXMLの要素のスーパクラス

    """
    def __init__(self, parent, blxml, root=None):
        """XMLBase のコンストラクタ
        """
        if root is None:
            self._root = parent.root()
        else:
            self._root = root
        self._parent = parent
        self._blxml = blxml

    def parent(self, p=None):
        """parent の取得・設定

        """
        if p is not None:
            self._parent = p
        return self._parent

    def blxml(self, x=None):
        """BLXML の取得・設定

        """
        if x is not None:
            self._blxml = x
        return self._blxml

    def root(self, r=None):
        """root の取得・設定

        """
        if r is not None:
            self._root = r
        return self._root


    def correct(self):
        """要素の適正化

        これは各サブクラスで定義する
        """


class Root(ElementBase):
    """トップレベルの <blocks> のクラス

    """
    def __init__(self, blxml):
        """Rootのコンストラクタ

        """
        super().__init__(self, blxml, self)
        self._blockMap = {}
        self._portMap = {}
        self._functionBlockMap = {}
        self._blockFunctionMap = {}
        self._blockRecordMap = {}
        self._typenameBlockMap = {}
        self._tagnameBlockMap = {}
        self._source_streams = {}
        self.children = []
        for b in blxml.get_block():
            self.children.append(CodeBlock.factory(self, b, ''))
        for b in self.children:
            b.correct()

        # clang-ast の <file> の連想配列の読み込み
        clang_ast = None
        for f in blxml.get_file():
            file_type = f.get_type()
            if file_type == 'clang-ast':
                self.loadMap(f)
            elif file_type == 'c-source':
                self._source_streams[f.get_name()] = io.StringIO()

    def loadMap(self, clang_ast):
        """clang_astのマップ読み込み

        """
        fbMap = None
        brMap = None
        for m in clang_ast.get_map():
            if m.get_name() == 'astFuncBlockMap':
                fbMap = m
            elif m.get_name() == 'astBlockRecordMap':
                brMap = m
            if fbMap is not None and brMap is not None:
                break

        # 関数-ブロック名のマップ情報
        if fbMap is not None:
            for k in fbMap.get_key():
                fname = k.get_name()
                mval = self._functionBlockMap.get(fname)
                if mval is None:
                    mval = []
                    self._functionBlockMap[fname] = mval

                for v in k.get_value():
                    qualType = v.get_type()
                    blockName = v.get_valueOf_()

                    # 結局のところ、最内の()が関数のパラメタのはずである。
                    paren = None
                    pend = None
                    for i, char in enumerate(qualType):
                        if char == '(':
                            paren = i
                        elif char == ')':
                            pend = i + 1
                            break
                    if paren is not None:
                        proto = qualType[:paren] + fname + qualType[paren:]
                        func = fname + qualType[paren:pend]
                    else:
                        proto = fname
                        func = fname
                    r = [qualType, func, proto, blockName]

                    mval.append(r)
                    self._blockFunctionMap[blockName] = r

        # ブロック名-レコードのマップ情報。

        # 例えば class A の場合、typename は 'A',
        # tagname は 'class A' である。
        if brMap is not None:
            for k in brMap.get_key():
                blockName = k.get_name()
                tmap = self._blockRecordMap.get(blockName)
                if tmap is None:
                    tmap = {}
                    self._blockRecordMap[blockName] = tmap
                for v in k.get_value():
                    t = v.get_type()
                    n = v.get_valueOf_()
                    tmap[t] = n
                    if t == 'typename':
                        self._typenameBlockMap[n] = blockName
                    elif t == 'tagname':
                        self._tagnameBlockMap[n] = blockName

    def blockMap(self, blockName=None, xmlBlock=None):
        """blockMap の取得・登録

        """
        if xmlBlock is not None:
            self._blockMap[blockName] = xmlBlock
        return self._blockMap

    def portMap(self, portName=None, xmlPort=None):
        """portMap の取得・登録

        """
        if xmlPort is not None:
            self._portMap[portName] = xmlPort
        return self._portMap

    def getBlock(self, blockName):
        """Block の取得

        """
        b = self._blockMap.get(blockName)
        if b is None:
            print(f'Error: Block {blockName} undefined', file=sys.stderr)
            sys.exit(1)
        return b

    def getPort(self, portName):
        """Input/Output の取得

        """
        p = self._portMap.get(portName)
        if p is None:
            print(f'Error: Port {portName} undefined', file=sys.stderr)
            sys.exit(1)
        return p

    def functionBlockMap(self, funcName=None, qualType=None):
        """funcName を探す、または _functionBlockMap を返す

        funcName が指定され qualType が指定されている場合は、
        一致する関数の情報が返される。
        これは以下のようになっている。

          ['int (int)', 'func(int)', 'int func(int)', 'blockName' ]

        また、qualType が指定されていない場合は、関数名が一致するもの
        全て(上記のリスト)が返される。

        funcName が指定されていない場合は dict が返される。

        """
        if funcName is not None:
            mval = self._functionBlockMap.get(funcName)
            if qualType is None:
                return mval
            for v in mval:
                if qualType == v[0]:
                    return v
            return None
        return self._functionBlockMap

    def blockFunctionMap(self, blockName=None):
        """blockName に対応する関数を探す、または _blockFunctionMap を返す

        """
        if blockName is not None:
            return self._blockFunctionMap.get(blockName)
        return self._blockFunctionMap

    def blockRecordMap(self, blockName=None, recordType=None):
        """blockName に対する CXXRecordDecl に相当するものを返す

        recordType は 'typename' または 'tagname' である。
        'typename' は、構造体等に指定されるタグ名である。
        'tagname' は構造体などのタグを含むものである。
        例えば class A であれば、前者は 'A' 後者は 'class A' である。

        blockName が指定されている場合で
        recordType が指定されている場合は、
        対応するもの(str)を返す

        また recordType が指定されていない場合は、
        例えば以下のような dict が返る。

          { 'typename' : 'A', 'tagname' : 'class A' }

        blockName が指定されていない場合、
        blockName をキーとした全体の dict が返る

        """
        if blockName is not None:
            tmap = self._blockRecordMap.get(blockName)
            if recordType is None:
                return tmap
            if tmap is not None:
                return tmap.get(recordType)
            return None
        return self._blockRecordMap

    def typenameBlockMap(self, typeName=None):
        """typeName に一致するブロックまたは _typenameBlockMap を返す

        """
        if typeName is not None:
            return self._typenameBlockMap.get(typeName)
        return self._typenameBlockMap

    def tagnameBlockMap(self, tagName=None):
        """tagName に一致するブロックまたは _tagnameBlockMap を返す

        """
        if tagName is not None:
            return self._tagnameBlockMap.get(tagName)
        return self._tagnameBlockMap


    def source_streams(self, file_name=None, file_stream=None):
        """ファイル名に対する出力ストリームの設定・取得

        """
        if file_name is None:
            return self._source_streams
        if file_stream is not None:
            self._source_streams[file_name] = file_stream
            return file_stream
        return self._source_streams.get(file_name)


class Connect(ElementBase):
    """Connectのクラス

    <input>/<output> の <connect> に対応する

    """
    def __init__(self, parent, blxml):
        """Connect のコンストラクタ
        """
        super().__init__(parent, blxml)
        self.blockName = blxml.get_block()
        self.portName = blxml.get_port()
        self.block = None
        self.port = None

    def correct(self):
        """Connect の適正化

        """
        self.block = self.root().getBlock(self.blockName)
        self.port = self.root().getPort(self.portName)


class IOPortBase(ElementBase):
    """<input>, <output> のスーパクラス

    """
    def __init__(self, parent, blxml):
        """IOPortBase のコンストラクタ
        """
        super().__init__(parent, blxml)
        self.blockName = parent.blockName
        self.line = blxml.get_line()
        self.portName = blxml.get_port()
        self._connect = []
        for c in blxml.get_connect():
            self._connect.append(Connect(self, c))
        self.root().portMap(self.portName, self)

    def connect(self, c=None):
        """connect の設定・取得

        """
        if c is not None:
            if isinstance(c, list):
                self._connect.extend(c)
            else:
                self._connect.append(c)
        return self._connect

    def correct(self):
        """要素の適正化

        """
        for c in self._connect:
            c.correct()


class Input(IOPortBase):
    """BLXMLの<input>のクラス

    """


class Output(IOPortBase):
    """BLXMLの<output>のクラス

    """


class Var(ElementBase):
    """BLXML の <var> のクラス

    """

    def __init__(self, parent, blxml):
        """Var のコンストラクタ

        """
        super().__init__(parent, blxml)
        self.varName = blxml.get_name()
        self.line = blxml.get_line()
        self.mode = blxml.get_mode()
        self.portName = blxml.get_port()
        self.port = None

    def correct(self):
        """要素の適正化

        """
        self.port = self.root().getPort(self.portName)


class LinkBase(ElementBase):
    """<forward>/<backward> のスーパークラス

    """

    def __init__(self, parent, blxml):
        """LinkBase のコンストラクタ
        """
        super().__init__(parent, blxml)
        self.blockName = blxml.get_block()
        self.block = None
        self.var = {}
        for v in blxml.get_var():
            varName = v.get_name()
            self.var[varName] = Var(self, v)

    def correct(self):
        """要素の適正化

        """
        self.block = self.root().getBlock(self.blockName)
        for v in self.var.values():
            v.correct()


class Forward(LinkBase):
    """BLXMLの<forward>のクラス

    """


class Backward(LinkBase):
    """BLXMLの<backward>のクラス

    """

class Function(LinkBase):
    """BLXMLの<backward>のクラス

    """

class CodeBlock(ElementBase):
    """BLXMLの<block>のクラス

    """

    def __init__(self, parent, blxml, indent='', subclass=None):
        """Block のコンストラクタ

        """
        global verbose
        if verbose > 0:
            if subclass is None:
                print(f'- {indent}Create Block : {blxml.get_name()}')
            else:
                print(f'- {indent}Create ' \
                      f'{subclass.__class__.__name__} : ' \
                      f'{blxml.get_name()}')
        super().__init__(parent, blxml)
        self.blockName = blxml.get_name()
        self.root().blockMap(self.blockName, self)
        self.peinfo = blxml.get_peinfo()
        self.input = []
        self.output = []
        self.inputVar = {}
        self.outputVar = {}
        self.code = []          # これには code_T がそのまま入る
        self.forward = []
        self.backward = []
        self.function = []
        self.threads = []
        self.joins = []
        self.need_context = False

        for i in blxml.get_input():
            self.input.append(Input(self, i))
        for o in blxml.get_output():
            self.output.append(Output(self, o))
        for v in blxml.get_var():
            var = Var(self, v)
            if var.mode == 'input':
                self.inputVar[var.varName] = var
            else:
                self.outputVar[var.varName] = var
        for c in blxml.get_code():
            self.code.append(c)
        for f in blxml.get_forward():
            self.forward.append(Forward(self, f))
        for b in blxml.get_backward():
            self.backward.append(Backward(self, b))
        for f in blxml.get_function():
            self.function = f.name

    def correct(self):
        """要素の適正化

        """
        for i in self.input:
            i.correct()
        for o in self.output:
            o.correct()
        for f in self.forward:
            f.correct()
        for b in self.backward:
            b.correct()

    def listParents(self):
        """親のリストを近い順に取得する。

        ただし Root は含まない。

        """
        cur = self.parent()
        r = []
        while not isinstance(cur, Root):
            r.append(cur)
            cur = cur.parent()
        return r

    def commonParent(self, block):
        """共通の親を探す

        最初が自分、次が指定した block の親のリスト。
        親のリストは近い順に並ぶ。
        それぞれの [-1] が共通の親である。

        ただし Root は含まない。

        """
        blockParents = block.listParents()
        myParents = []
        cur = self.parent()
        while not isinstance(cur, Root):
            myParents.append(cur)
            if cur in blockParents:
                i = blockParents.index(cur)
                return myParents, blockParents[:i + 1]
            cur = cur.parent()
        return None, None

    @staticmethod
    def factory(parent, blxml, indent):
        """Block のサブクラスを作成する

        """
        subclass = {
            'SubSystem' : SubSystem,
            'CombinedBlock' : CombinedBlock,
            'CallBlock' : CallBlock,
            'Inport' : Inport,
            'Outport' : Outport
        }
        blockType = blxml.get_blocktype()
        if blockType in subclass:
            subcls = subclass[blockType]
            return subcls(parent, blxml, indent)
        return CodeBlock(parent, blxml, indent)


class SubSystem(CodeBlock):
    """SubSystem のクラス

    """

    # FunctionDecl の仲間
    #
    # この仲間の SubSystem の場合、
    # 最初の CombinedBlock の後がスコープになる
    FuncDeclTypes = ['FunctionDecl', 'CXXConstructorDecl',
                     'CXXDestructorDecl', 'CXXMethodDecl', 'CXXConstructorDecl']

    # ステートメント
    #
    # この仲間の場合、このSubSystemの外のスコープを使う必要がある。
    StatementTypes = ['CompoundStmt', 'IfStmt', 'ElseStmt',
                      'SwitchStmt', 'WhileStmt', 'ForStmt', 'DoStmt',
                      'CXXTryStmt', 'CXXCatchStmt', 'CXXForRangeStmt']

    def __init__(self, parent, blxml, indent):
        """SubSystem のコンストラクタ

        """
        super().__init__(parent, blxml, indent, self)
        self.isFuncDecl = False

        astInfoMap = None
        for m in blxml.get_map():
            if m.get_name() == 'astInfo':
                astInfoMap = m
                break

        if astInfoMap is not None:
            for k in astInfoMap.get_key():
                key = k.get_name()
                if key == 'classType':
                    self.classType = k.get_value()[0].get_valueOf_()
                    if self.classType in self.FuncDeclTypes:
                        self.isFuncDecl = True

        self.children = []
        bslist = blxml.get_blocks()
        if bslist:
            for b in bslist[0].get_block():
                self.children.append(CodeBlock.factory(self, b, indent + '  '))


    def correct(self):
        """要素の適正化

        """
        for b in self.children:
            b.correct()


class OrdinalBlock(CodeBlock):
    """一般のブロック

    """

    def __init__(self, parent, blxml, indent):
        """CombinedBlock のコンストラクタ

        """
        super().__init__(parent, blxml, indent, self)

class CombinedBlock(OrdinalBlock):
    """CombinedBlock のクラス

    """


class CallBlock(CodeBlock):
    """CallBlock のクラス

    """


class Inport(OrdinalBlock):
    """Inport のクラス

    """


class Outport(OrdinalBlock):
    """Outport のクラス

    """

class SimulinkBlock(ElementBase):
    def __init__(self, block):
        self.blockName = block.get_name()
        self.blockType = block.get_blocktype()
        self.input = []
        self.output = []
        self.code = []

        for i in block.get_input():
            self.input.append(i)
        for o in block.get_output():
            self.output.append(o)
        for c in block.get_code():
            self.code.append(c)
    