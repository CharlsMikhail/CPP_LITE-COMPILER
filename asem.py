from numpy import number
from prettytable import PrettyTable
import asin


class node_scope_stack:

  def __init__(self, type, name, scope, flag):
    self.type = type
    self.name = name
    self.scope = scope
    self.flag = flag
    self.parm = 0
    self.idfunc = None

  def to_list(self):
    return [
        self.type, self.name, self.scope, self.flag, self.parm, self.idfunc
    ]


rootP = asin.asin()
numParms = 0
stackScope = []
scopeCurrent = "global"
tabla = PrettyTable(["Type", "Name", "Scope", "Flag", "Parms", "ID Function"])


def printStack():
  global stackScope
  tabla.clear_rows()
  print("Las tabla(PILA) de ambito de funciones y variables es:\n")
  for node in reversed(stackScope):
    tabla.add_row(node.to_list())
  print(tabla)


def verificarExistenciaEnPila(name, scope, parms=0):
  global stackScope
  print("nombre:", name)
  print("scope:", scope)
  print("parms:", parms)
  for nodex in stackScope:
    if nodex.name == name and nodex.scope == scope and nodex.parm == parms:
      if nodex.idfunc is not None:
        return nodex.idfunc
      else:
        return True
  return False


def borrarEnPila():
  global stackScope
  global scopeCurrent
  for nodex in reversed(stackScope):
    if nodex.scope == scopeCurrent:
      stackScope.pop()
    else:
      return


def contarParametrosFuncion(node, parent_symbol=None):
  global numParms
  if node is not None:
    if node.symbol == 'ID':
      numParms += 1
    for child in reversed(node.children):
      contarParametrosFuncion(child, node.symbol)


def verificarArgumentosFuncion(node, parent_symbol=None):
  global scopeCurrent
  global numParms
  if node is not None:
    if node.symbol == 'ARGUMENT_FUNC':
      numParms += 1
    if node.symbol == "ID":
      if verificarExistenciaEnPila(node.lexeme, scopeCurrent) is False:
        print("\nError Semantico(ES-01): la Variable '" + node.lexeme,
              "' no fue declarada en el scope: " + scopeCurrent)
        exit()
    for child in reversed(node.children):
      verificarArgumentosFuncion(child, node.symbol)


def reconocerFunciones(node, parent_symbol=None):
  if node is not None:
    if parent_symbol == "FUNC" and node.symbol == "ID":
      global stackScope
      # Función con tipo de retorno ~void
      if (node.father.children[-1].symbol == "TYPE_ID"):
        print("TIPO X")
        stackF = node_scope_stack(node.father.children[-1].children[-1].lexeme,
                                  node.lexeme, "global", "function")
      else:
        print("TIPO VOID")
        # Función con tipo de retorno void
        stackF = node_scope_stack(node.father.children[-1].lexeme, node.lexeme,
                                  "global", "function")
      global numParms
      contarParametrosFuncion(node.father.children[-4])
      stackF.parm = numParms
      stackF.idfunc = node.father
      numParms = 0

      if (verificarExistenciaEnPila(stackF.name, stackF.scope, stackF.parm)
          is not False):
        print("\nError Semantico(ES-02): La Funcion '" + stackF.name +
              "' ya fue definida.")
        exit(1)
      else:

        stackScope.append(stackF)
    for child in reversed(node.children):
      if child.symbol == 'MAIN':
        global scopeCurrent
        scopeCurrent = 'run'
        reconocerVariablesMain(node.children[4])
        return
      reconocerFunciones(child, node.symbol)


def reconocerVariablesMain(node, parent_symbol=None):
  if node is not None:
    # Todo gira en torno al TOKEN: 'ID'  y en cualquien caso verificar el ambito(Pila).
    if node.symbol == "ID":
      global scopeCurrent
      global stackScope
      # Verificar si es una variable que se esta definiendo: TYPE_ID
      if node.father.children[-1].symbol == "TYPE_ID":
        stackF = node_scope_stack(node.father.children[-1].children[-1].lexeme,
                                  node.lexeme, scopeCurrent, "variable")
        if (verificarExistenciaEnPila(stackF.name, stackF.scope) == True):
          print("\nError Semantico(ES-03): La Variable '" + stackF.name +
                "' ya fue definida en: " + stackF.scope)
          exit(1)
        else:
          stackScope.append(stackF)
      # Verificar si es una funcion en uso: FUNCK_OR_EQUAL | INVOKER_FUNK ---> PARIZQ ID PARDER
      elif ((node.father.children[0].symbol == "FUNC_OR_EQUAL"
             or node.father.children[0].symbol == "INVOKER_FUNC")
            and node.father.children[0].children[-1].symbol == "PAR_LEFT"):
        global numParms
        numParms = 0
        verificarArgumentosFuncion(node.father.children[0])
        print(node.lexeme, " es una funcion y tiene ", numParms, " parametros")
        verdad_and_node = verificarExistenciaEnPila(node.lexeme, 'global',
                                                    numParms)
        print("aea: ", verdad_and_node)
        print("nod: ", node.lexeme)
        if (verdad_and_node == False):
          print("\nError Semantico(ES-04): La Funcion '" + node.lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
          exit(1)
        else:  # Si es asi entonces ir a RVF(node, parent);
          scopeCurrent = node.lexeme
          reconocerParametrosFunc(verdad_and_node.children[-4])
          reconocerVariablesFunc(verdad_and_node.children[-7])
          if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
            print("HOLAAAAAAAAAAAAAAAAAA")
            reconocerVariablesReturnFunc(verdad_and_node.children[-9])
          printStack()
          borrarEnPila()
          printStack()
          scopeCurrent = 'run'
      # Verificar si es una variable en uso: CALCULATOR
      else:
        if (verificarExistenciaEnPila(node.lexeme, scopeCurrent) == False):
          print("\nError Semantico(ES-05): La Variable '" + node.lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)

    for child in reversed(node.children):
      reconocerVariablesMain(child, node.symbol)


def reconocerParametrosFunc(node, parent_symbol=None):
  if node is not None:
    global stackScope
    global scopeCurrent
    if parent_symbol == "PARAMETER_FUNC" and node.symbol == "ID":
      stackF = node_scope_stack(node.father.children[-1].children[-1].lexeme,
                                node.lexeme, scopeCurrent, "variable")
      if (verificarExistenciaEnPila(stackF.name, stackF.scope) == True):
        print("\nError Semantico(ES-06): La Variable '" + stackF.name +
              "' ya fue definida en: " + stackF.scope)
        exit(1)
      else:
        stackScope.append(stackF)
    for child in reversed(node.children):
      reconocerParametrosFunc(child, node.symbol)


def reconocerVariablesReturnFunc(node, parent_symbol=None):
  global scopeCurrent
  global stackScope
  if node is not None:
    if node.symbol == "ID":
      # Verificar si es una funcion en uso: FUNCK_OR_EQUAL | INVOKER_FUNK ---> PARIZQ ID PARDER
      if ((node.father.children[0].symbol == "FUNC_OR_EQUAL"
           or node.father.children[0].symbol == "INVOKER_FUNC")
          and node.father.children[0].children[-1].symbol == "PAR_LEFT"):
        global numParms
        numParms = 0
        verificarArgumentosFuncion(node.father.children[0])
        verdad_and_node = verificarExistenciaEnPila(node.lexeme, scopeCurrent,
                                                    numParms)
        if (verdad_and_node == False):
          print("\nError Semantico(ES-07): La Funcion '" + node.lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
          exit(1)
        else:  # Si es asi entonces ir a RVF(node, parent);
          print("JAJAJAJA")
          copyScopeCurrent = scopeCurrent
          scopeCurrent = node.lexeme
          reconocerParametrosFunc(verdad_and_node.children[-4])
          reconocerVariablesFunc(verdad_and_node.children[-7])
          if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
            reconocerVariablesReturnFunc(verdad_and_node.children[-9])
          borrarEnPila()
          printStack()
          scopeCurrent = copyScopeCurrent
      # Verificar si es una variable en uso: CALCULATOR
      else:
        if (verificarExistenciaEnPila(node.lexeme, scopeCurrent) == False):
          print("\nError Semantico(ES-08): La Variable '" + node.lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)
    for child in reversed(node.children):
      reconocerVariablesReturnFunc(child, node.symbol)


def reconocerVariablesFunc(node, parent_symbol=None):
  global scopeCurrent
  global stackScope
  if node is not None:
    if node.symbol == "ID":
      # Verificar si es una variable que se esta definiendo: TYPE_ID
      if node.father.children[-1].symbol == "TYPE_ID":
        stackF = node_scope_stack(node.father.children[-1].children[-1].lexeme,
                                  node.lexeme, scopeCurrent, "variable")
        if (verificarExistenciaEnPila(stackF.name, stackF.scope) == True):
          print("\nError Semantico(ES-09): La Variable '" + stackF.name +
                "' ya fue definida en: " + stackF.scope)
          exit(1)
        else:
          stackScope.append(stackF)
      # Verificar si es una funcion en uso: FUNCK_OR_EQUAL | INVOKER_FUNK ---> PARIZQ ID PARDER
      elif ((node.father.children[0].symbol == "FUNC_OR_EQUAL"
             or node.father.children[0].symbol == "INVOKER_FUNC")
            and node.father.children[0].children[-1].symbol == "PAR_LEFT"):
        global numParms
        numParms = 0
        verificarArgumentosFuncion(node.father.children[0])
        verdad_and_node = verificarExistenciaEnPila(node.lexeme, scopeCurrent,
                                                    numParms)
        if (verdad_and_node == False):
          print("\nError Semantico(ES-10): La Funcion '" + node.lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
          exit(1)
        else:  # Si es asi entonces ir a RVF(node, parent);
          print("JAJAJAJA")
          copyScopeCurrent = scopeCurrent
          scopeCurrent = node.lexeme
          reconocerParametrosFunc(verdad_and_node.children[-4])
          reconocerVariablesFunc(verdad_and_node.children[-7])
          if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
            reconocerVariablesReturnFunc(verdad_and_node.children[-9])
          borrarEnPila()
          printStack()
          scopeCurrent = copyScopeCurrent
      # Verificar si es una variable en uso: CALC
      # Verificar si es una variable en uso: CALCULATOR
      else:
        if (verificarExistenciaEnPila(node.lexeme, scopeCurrent) == False):
          print("\nError Semantico(ES-11): La Variable '" + node.lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)
    for child in reversed(node.children):
      reconocerVariablesFunc(child, node.symbol)


reconocerFunciones(rootP)

separador = "-" * 60
print(separador)
print("Test Analizador Semantico: Passed :)")
printStack()
print(separador)
