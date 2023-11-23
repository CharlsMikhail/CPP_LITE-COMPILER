from numpy import number
from prettytable import PrettyTable
import asin

# Regla de inferencia de tipos:

subtypes = {
    "bl": [],
    "dbl": ["it"],
    "it": ["bl"],
    "str": ["ch"],
    "ch": ["bl"],
    "vd": []
}


def definirTipo(tipo1, tipo2):
  print("TIPO1: ", tipo1)
  print("TIPO2: ", tipo2)
  if tipo1 == tipo2:
    return tipo1

  def buscar_subtipo(tipo_actual, tipo_objetivo):
    if tipo_actual == tipo_objetivo:
      return True
    for subtipo in subtypes.get(tipo_actual, []):
      if buscar_subtipo(subtipo, tipo_objetivo):
        return True
    return False

  if buscar_subtipo(tipo1, tipo2):
    return tipo1

  if buscar_subtipo(tipo2, tipo1):
    return tipo2
  return None


def tipo_resultante(tipo1, tipo2, operador):
  print("tipo 1", tipo1)
  print("tipo 2", tipo2)
  print("operador", operador)

  TypeFinal = definirTipo(tipo1, tipo2)

  if (operador in ('+', '-', '*', '/')) and (TypeFinal in ('dbl', 'it')):
    return TypeFinal
  elif (operador in ('>', '<', '>=', '<=')) and (TypeFinal in ('dbl', 'it')):
    return 'bl'
  elif (operador in ('==', '!=')) and (TypeFinal
                                       in ('dbl', 'it', 'bl', 'ch', 'str')):
    return 'bl'
  elif (operador in ('&', '|')) and (TypeFinal == 'bl'):
    return 'bl'
  elif (operador == '+') and (TypeFinal == 'str'):
    return 'str'
  else:
    print("\nError Semantico(ES-01-TYPE): Operacion: '", tipo1, operador,
          tipo2, "' no es valida")
    exit(1)


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


#FUNCIONES AUXILIARES
def printStack():
  global stackScope
  tabla.clear_rows()
  print("Las tabla(PILA) de ambito de funciones y variables es:\n")
  for node in reversed(stackScope):
    tabla.add_row(node.to_list())
  print(tabla)


nombre_archivo = "arbolSintaticoFinal.txt"
archivo = open(nombre_archivo, "w")
padres_impresos = []


def imprimir_arbol_preorden_inverso(node, padre=None):
  if node is not None:
    for child in reversed(node.children):
      imprimir_arbol_preorden_inverso(child, node)
    if padre is not None:
      if len(node.children) == 0:
        archivo.write(
            f"{node.id} [style = filled fillcolor= yellow label = <Symbol: {node.symbol}<BR/>Lexeme: '{node.lexeme}'<BR/>DataType: '{node.type}'>]\n"
        )
      if padre.id not in padres_impresos:
        archivo.write(
            f"{padre.id} [style = filled fillcolor= gray label = <Symbol: {padre.symbol}<BR/>Lexeme: '{padre.lexeme}'<BR/>DataType: '{padre.type}'>]\n"
        )
        padres_impresos.append(padre.id)
      archivo.write(f"{padre.id} -> {node.id}\n")


def verificarExistenciaEnPila(name, scope, parms=0):
  global stackScope
  for nodex in stackScope:
    if nodex.name == name and nodex.scope == scope and nodex.parm == parms:
      if nodex.idfunc is not None:
        return nodex.idfunc
      else:
        return nodex
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
    if node.symbol == 'ARGUMENT_FUNC' and node.children[-1].symbol != 'e':
      numParms += 1
    if node.symbol == "ID":
      if verificarExistenciaEnPila(node.lexeme, scopeCurrent) is False:
        print("\nError Semantico(ES-01): la Variable '" + node.lexeme,
              "' no fue declarada en el scope: " + scopeCurrent)
        exit(1)
    for child in reversed(node.children):
      verificarArgumentosFuncion(child, node.symbol)


def verificarTiposCalculator(node, actualType):
  global numParms
  global scopeCurrent
  if node is not None:
    ##print("SIMBOLO:", node.symbol)
    if node.symbol == "OPERATION" and node.children[-1].symbol != 'e':
      #PARENTESIS
      if node.children[-2].children[-1].symbol == 'PAR_LEFT':
        print(actualType[-1])
        print("ENTRE A PARENTESIS")
        '''if(node.children[-2].children[-2].children[-1].children[-2].symbol ==)

      else:'''
        ###########################################################################
        if (node.children[-2].children[-2].children[-1].children[-1].symbol ==
            'ID'):
          #INVOCACION DE FUNCIONES
          if (node.children[-2].children[-2].children[-1].children[-2].
              children[-1].symbol == 'PAR_LEFT'):
            numParms = 0
            verificarArgumentosFuncion(node.children[-2].children[-2].
                                       children[-1].children[-2].children[-2])
            verdad_and_node = verificarExistenciaEnPila(
                node.children[-2].children[-2].children[-1].children[-1].
                lexeme, 'global', numParms)
            if (verdad_and_node == False):
              print(numParms)
              print(
                  "\nError Semantico(ES-04-CAL-1): La Funcion '" + node.
                  children[-2].children[-2].children[-1].children[-1].lexeme +
                  "' no esta definida o no tiene el mismo número de parametros."
              )
              exit(1)
            else:  # Si es asi entonces ir a RVF(node, parent);
              scopeCurrent = node.children[-2].children[-2].children[
                  -1].children[-1].lexeme
              reconocerParametrosFunc(verdad_and_node.children[-4])
              reconocerVariablesFunc(verdad_and_node.children[-7])
              if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
                reconocerVariablesReturnFunc(verdad_and_node.children[-9])
              printStack()
              borrarEnPila()
              printStack()
              scopeCurrent = 'run'
              if (verdad_and_node.children[-1].symbol == 'TYPE_VOID'):
                print(
                    "\nError Semantico(ES-04-CALC-234): No se puede operar con una función tipo VOID"
                )
              exit(1)
            actualType[-1] = tipo_resultante(
                actualType[-1],
                verdad_and_node.children[-1].children[-1].lexeme,
                node.children[-1].lexeme)
          #USO DE ID
          else:
            IDCurrent = verificarExistenciaEnPila(
                node.children[-2].children[-2].children[-1].children[-1].
                lexeme, scopeCurrent)
            if (IDCurrent == False):
              print("\nError Semantico(ES-05-2): La Variable '" +
                    node.children[-2].children[-2].children[-1].children[-1].
                    lexeme + "' no esta definida en el scope: " + scopeCurrent)
              exit(1)
            else:
              actualType[-1] = tipo_resultante(actualType[-1], IDCurrent.type,
                                               node.children[-1].lexeme)
      ###########################################################################
        else:
          print(node.children[-2].children[-2].children[-1].children[-1].type)

          actualType.append(
              node.children[-2].children[-2].children[-1].children[-1].type)
          print("NODO ENVIADO POR PAR", node.children[-2].symbol)
          verificarTiposCalculator(node.children[-2], actualType)
          print("Tipo actual: ", actualType[-1])

          actualType.append(
              tipo_resultante(actualType.pop(), actualType[-1],
                              node.children[-1].lexeme))
          print("Tipo actual2: ", actualType[-1])
          print("SALI del PARENTEISSI")
          #tendria que invocar a la funcion verificarTiposCalculator con el hijo[-2]
          #ademas tengo que ahora jugar con el inidice ++
          #al volver tengo que verificar con el inidice anterior, verificar tipos.
      elif (node.children[-2].children[-1].symbol == 'ID'):
        #INVOCACION DE FUNCIONES
        if (node.children[-2].children[-2].children[-1].symbol == 'PAR_LEFT'):
          numParms = 0
          verificarArgumentosFuncion(
              node.children[-2].children[-2].children[-2])
          verdad_and_node = verificarExistenciaEnPila(
              node.children[-2].children[-1].lexeme, 'global', numParms)
          if (verdad_and_node == False):
            print(numParms)
            print(
                "\nError Semantico(ES-04-CAL-OJO): La Funcion '" +
                node.children[-2].children[-1].lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
            exit(1)
          else:  # Si es asi entonces ir a RVF(node, parent);
            scopeCurrent = node.children[-2].children[-1].lexeme
            reconocerParametrosFunc(verdad_and_node.children[-4])
            reconocerVariablesFunc(verdad_and_node.children[-7])
            if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
              reconocerVariablesReturnFunc(verdad_and_node.children[-9])
            printStack()
            borrarEnPila()
            printStack()
            scopeCurrent = 'run'
            if (verdad_and_node.children[-1].symbol == 'TYPE_VOID'):
              print(
                  "\nError Semantico(ES-04-CALC-1): No se puede operar con una función tipo VOID"
              )
              exit(1)
          actualType[-1] = tipo_resultante(
              actualType[-1], verdad_and_node.children[-1].children[-1].lexeme,
              node.children[-1].lexeme)
        #USO DE ID
        else:
          IDCurrent = verificarExistenciaEnPila(
              node.children[-2].children[-1].lexeme, scopeCurrent)
          if (IDCurrent == False):
            print("\nError Semantico(ES-05-2): La Variable '" +
                  node.children[-2].children[-1].lexeme +
                  "' no esta definida en el scope: " + scopeCurrent)
            exit(1)
          else:
            actualType[-1] = tipo_resultante(actualType[-1], IDCurrent.type,
                                             node.children[-1].lexeme)

      #ARG NORMALES.
      else:
        actualType.append(node.children[-2].children[-1].type)
        actualType.append(
            tipo_resultante(actualType.pop(), actualType[-1],
                            node.children[-1].lexeme))

    for child in reversed(node.children):
      verificarTiposCalculator(child, actualType)


# FUNCIONES COMPUESTAS
def reconocerFunciones(node, parent_symbol=None):
  if node is not None:
    if parent_symbol == "FUNC" and node.symbol == "ID":
      global stackScope
      # Función con tipo de retorno ~void
      if (node.father.children[-1].symbol == "TYPE_ID"):
        stackF = node_scope_stack(node.father.children[-1].children[-1].lexeme,
                                  node.lexeme, "global", "function")
      else:
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
    # DECLARACION DE VARIABLES O INVOCACIONES FUERA DE CALCULATOR
    if node.symbol == "ID":
      global scopeCurrent
      global stackScope
      # Verificar si es una variable que se esta definiendo: TYPE_ID
      if node.father.children[-1].symbol == "TYPE_ID":
        print("aeaeaeaeaeaeaeasfaeaeaea")
        stackF = node_scope_stack(node.father.children[-1].children[-1].lexeme,
                                  node.lexeme, scopeCurrent, "variable")
        node.type = node.father.children[-1].children[-1].lexeme
        print("NODE TYPE DECLARATION", node.type)
        print("NODE LEXEME DECLARATION", node.lexeme)
        if (verificarExistenciaEnPila(stackF.name, stackF.scope) != False):
          print("\nError Semantico(ES-03): La Variable '" + stackF.name +
                "' ya fue definida en: " + stackF.scope)
          exit(1)
        else:
          stackScope.append(stackF)
      # Verificar si es una funcion en uso: FUNCK_OR_ASSIGN | INVOKER_FUNK ---> PARIZQ ID PARDER
      elif (node.father.children[0].symbol == "FUNC_OR_ASSIGN"
            and node.father.children[0].children[-1].symbol == "PAR_LEFT"):
        global numParms
        numParms = 0
        verificarArgumentosFuncion(node.father.children[0])
        verdad_and_node = verificarExistenciaEnPila(node.lexeme, 'global',
                                                    numParms)
        if (verdad_and_node == False):
          print("\nError Semantico(ES-04): La Funcion '" + node.lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
          exit(1)
        else:  # Si es asi entonces ir a RVF(node, parent);
          scopeCurrent = node.lexeme
          reconocerParametrosFunc(verdad_and_node.children[-4])
          reconocerVariablesFunc(verdad_and_node.children[-7])
          if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
            reconocerVariablesReturnFunc(verdad_and_node.children[-9])
          printStack()
          borrarEnPila()
          printStack()
          scopeCurrent = 'run'
      # Verificar si es una variable en uso: CALCULATOR
      else:
        #aqui iba lo de ID en USO
        pass
    # SI ENCUENTRO EXPRESIONES
    elif (node.symbol == 'CALCULATOR' and node.father.symbol != 'ARG'):
      #TIPO INICIAL ANTES DE MANDAR A INFERENCIA DE TIPOS.
      #aquiii es
      idCurr = None
      if (node.father.symbol == 'FUNC_OR_ASSIGN'):
        idCurr = verificarExistenciaEnPila(
            node.father.father.children[-1].lexeme, scopeCurrent)
        if (idCurr == False):
          print("\nError Semantico(ES-05-2-ID-SOLO): La Variable '" +
                node.father.father.children[-1].lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)

      if (node.children[-1].children[-1].symbol == 'ID'):
        #INVOCACION DE FUNCIONES
        if (node.children[-1].children[-2].symbol == "INVOKER_FUNC" and
            node.children[-1].children[-2].children[-1].symbol == "PAR_LEFT"):
          print("HOLAAAA ENTRE A INCIAL FUNCION APRA CALCULADORA")
          #global numParms
          numParms = 0
          verificarArgumentosFuncion(
              node.children[-1].children[-2].children[-2])
          verdad_and_node = verificarExistenciaEnPila(
              node.children[-1].children[-1].lexeme, 'global', numParms)
          if (verdad_and_node == False):
            print(
                "\nError Semantico(ES-04-MAIN-1): La Funcion '" +
                node.children[-1].children[-1].lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
            exit(1)
          else:  # Si es asi entonces ir a RVF(node, parent);
            scopeCurrent = node.children[-1].children[-1].lexeme
            reconocerParametrosFunc(verdad_and_node.children[-4])
            reconocerVariablesFunc(verdad_and_node.children[-7])
            if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
              reconocerVariablesReturnFunc(verdad_and_node.children[-9])
            printStack()
            borrarEnPila()
            printStack()
            scopeCurrent = 'run'
            if (verdad_and_node.children[-1].symbol == 'TYPE_VOID'):
              print(
                  "\nError Semantico(ES-04-MAIN-2): No se puede operar con una función tipo VOID"
              )
              exit(1)
            print("TIPO DE FUNC INCIAL:",
                  verdad_and_node.children[-1].children[-1].lexeme)
            actualType = [verdad_and_node.children[-1].children[-1].lexeme]
            verificarTiposCalculator(node, actualType)
            node.type = actualType[-1]
        #USO DE ID
        else:
          print(node.lexeme)
          IDCurrent = verificarExistenciaEnPila(
              node.children[-1].children[-1].lexeme, scopeCurrent)
          if (IDCurrent == False):
            print("\nError Semantico(ES-05-2): La Variable '" +
                  node.children[-1].children[-1].lexeme +
                  "' no esta definida en el scope: " + scopeCurrent)
            exit(1)
          else:
            print("LEXEMEEEEE1", node.children[-1].children[-1].lexeme)
            print("TIPOOOOOOOOOOOO1", IDCurrent.type)
            actualType = [IDCurrent.type]
            verificarTiposCalculator(node, actualType)
            node.type = actualType[-1]
      else:
        print("LEXEMEEEEE", node.children[-1].children[-1].lexeme)
        print("TIPOOOOOOOOOOOO", node.children[-1].children[-1].type)
        actualType = [node.children[-1].children[-1].type]
        verificarTiposCalculator(node, actualType)
        node.type = actualType[-1]
      # VERIFICACION DE TIPOS
      if node.father.symbol == 'ASSIGN_VAR':

        if definirTipo(node.type,
                       node.father.father.children[-2].type) != None:
          print("HAY COMPATIBILIDAD DE DATOS")
          #aqui falta hacer la asignacion de valores
        else:
          print("CALC",
                definirTipo(node.type, node.father.father.children[-2].type))
          print("ORIGINAL", node.father.father.children[-2].type)

          print(
              "\nError Semantico(ES-CAL): No hay compatibilidad de datos MAIN")
          exit(1)
      elif node.father.symbol == 'FUNC_OR_ASSIGN':
        if definirTipo(node.type,
                       idCurr.type) != None:
          print("HAY COMPATIBILIDAD DE DATOS")
          #aqui falta hacer la asignacion de valores
        else:
          print("CALC",
                definirTipo(node.type, idCurr.type))
          print(
              "\nError Semantico(ES-CAL-2): No hay compatibilidad de datos MAIN"
          )
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
      node.type = node.father.children[-1].children[-1].lexeme
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
      if (node.father.children[0].symbol == "FUNC_OR_ASSIGN"
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
          print("\nError Semantico(ES-08- FUNC): La Variable '" + node.lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)
    elif (node.symbol == 'CALCULATOR' and node.father.symbol != 'ARG'):
      #TIPO INICIAL ANTES DE MANDAR A INFERENCIA DE TIPOS.
      idCurr = None
      if (node.father.symbol == 'FUNC_OR_ASSIGN'):
        idCurr = verificarExistenciaEnPila(
            node.father.father.children[-1].lexeme, scopeCurrent)
        if (idCurr == False):
          print("\nError Semantico(ES-05-2-ID-SOLO): La Variable '" +
                node.father.father.children[-1].lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)
      if (node.children[-1].children[-1].symbol == 'ID'):
        #INVOCACION DE FUNCIONES
        if (node.children[-1].children[-2].symbol == "INVOKER_FUNC" and
            node.children[-1].children[-2].children[-1].symbol == "PAR_LEFT"):
          #global numParms
          numParms = 0
          verificarArgumentosFuncion(
              node.children[-1].children[-2].children[-2])
          verdad_and_node = verificarExistenciaEnPila(
              node.children[-1].children[-1].lexeme, 'global', numParms)
          if (verdad_and_node == False):
            print(
                "\nError Semantico(ES-04): La Funcion '" +
                node.children[-1].children[-1].lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
            exit(1)
          else:  # Si es asi entonces ir a RVF(node, parent);
            scopeCurrent = node.children[-1].children[-1].lexeme
            reconocerParametrosFunc(verdad_and_node.children[-4])
            reconocerVariablesFunc(verdad_and_node.children[-7])
            if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
              reconocerVariablesReturnFunc(verdad_and_node.children[-9])
            printStack()
            borrarEnPila()
            printStack()
            scopeCurrent = 'run'
            actualType = [verdad_and_node.children[-1].children[-1].lexeme]
            verificarTiposCalculator(node, actualType)
            node.type = actualType[-1]
        #USO DE ID
        else:
          print(node.lexeme)
          IDCurrent = verificarExistenciaEnPila(
              node.children[-1].children[-1].lexeme, scopeCurrent)
          if (IDCurrent == False):
            print("\nError Semantico(ES-05-2): La Variable '" +
                  node.children[-1].children[-1].lexeme +
                  "' no esta definida en el scope: " + scopeCurrent)
            exit(1)
          else:
            print("LEXEMEEEEE1", node.children[-1].children[-1].lexeme)
            print("TIPOOOOOOOOOOOO1", IDCurrent.type)
            actualType = [IDCurrent.type]
            verificarTiposCalculator(node, actualType)
            node.type = actualType[-1]
      else:
        print("LEXEMEEEEE", node.children[-1].children[-1].lexeme)
        print("TIPOOOOOOOOOOOO", node.children[-1].children[-1].type)
        actualType = [node.children[-1].children[-1].type]
        verificarTiposCalculator(node, actualType)
        node.type = actualType[-1]
      # VERIFICACION DE TIPOS RETUR
      if node.father.symbol == 'FUNC':
        if definirTipo(node.type,
                       node.father.children[-1].children[-1].lexeme) != None:
          print("HAY COMPATIBILIDAD DE DATOS")
          #aqui falta hacer la asignacion de valores
        else:
          print(
              "\nError Semantico(ES-CAL): No hay compatibilidad de datos -> RETURN"
          )
          exit(1)
      elif node.father.symbol == 'FUNC_OR_ASSIGN':
        if definirTipo(node.type,
                       idCurr.type) != None:
          print("HAY COMPATIBILIDAD DE DATOS")
          #aqui falta hacer la asignacion de valores
        else:
          print("CALC",
                definirTipo(node.type, idCurr.type))
          print(
              "\nError Semantico(ES-CAL-2): No hay compatibilidad de datos -> RETURN"
          )
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
        node.type = stackF.type
        if (verificarExistenciaEnPila(stackF.name, stackF.scope) != False):
          print("\nError Semantico(ES-09): La Variable '" + stackF.name +
                "' ya fue definida en: " + stackF.scope)
          exit(1)
        else:
          stackScope.append(stackF)
      # Verificar si es una funcion en uso: FUNCK_OR_EQUAL | INVOKER_FUNK ---> PARIZQ ID PARDER
      elif (node.father.children[0].symbol == "FUNC_OR_ASSIGN"
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
          copyScopeCurrent = scopeCurrent
          scopeCurrent = node.lexeme
          reconocerParametrosFunc(verdad_and_node.children[-4])
          reconocerVariablesFunc(verdad_and_node.children[-7])
          if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
            reconocerVariablesReturnFunc(verdad_and_node.children[-9])
          borrarEnPila()
          scopeCurrent = copyScopeCurrent
      # Verificar si es una variable en uso: CALC
      # Verificar si es una variable en uso: CALCULATOR
      else:
        pass
    elif (node.symbol == 'CALCULATOR' and node.father.symbol != 'ARG'):
      print("jajajajajajajajajajajajajjaja")
      idCurr = None
      if (node.father.symbol == 'FUNC_OR_ASSIGN'):
        idCurr = verificarExistenciaEnPila(
            node.father.father.children[-1].lexeme, scopeCurrent)
        if (idCurr == False):
          print("\nError Semantico(ES-05-2-ID-SOLO): La Variable '" +
                node.father.father.children[-1].lexeme +
                "' no esta definida en el scope: " + scopeCurrent)
          exit(1)
      
      #TIPO INICIAL ANTES DE MANDAR A INFERENCIA DE TIPOS.
      if (node.children[-1].children[-1].symbol == 'ID'):
        #INVOCACION DE FUNCIONES
        if (node.children[-1].children[-2].symbol == "INVOKER_FUNC" and
            node.children[-1].children[-2].children[-1].symbol == "PAR_LEFT"):
          #global numParms
          numParms = 0
          verificarArgumentosFuncion(
              node.children[-1].children[-2].children[-2])
          verdad_and_node = verificarExistenciaEnPila(
              node.children[-1].children[-1].lexeme, 'global', numParms)
          if (verdad_and_node == False):
            print(
                "\nError Semantico(ES-04): La Funcion '" +
                node.children[-1].children[-1].lexeme +
                "' no esta definida o no tiene el mismo número de parametros.")
            exit(1)
          else:  # Si es asi entonces ir a RVF(node, parent);
            scopeCurrent = node.children[-1].children[-1].lexeme
            reconocerParametrosFunc(verdad_and_node.children[-4])
            reconocerVariablesFunc(verdad_and_node.children[-7])
            if (verdad_and_node.children[-9].symbol == "CALCULATOR"):
              reconocerVariablesReturnFunc(verdad_and_node.children[-9])
            printStack()
            borrarEnPila()
            printStack()
            scopeCurrent = 'run'
            actualType = [verdad_and_node.children[-1].children[-1].lexeme]
            verificarTiposCalculator(node, actualType)
            node.type = actualType[-1]
        #USO DE ID
        else:
          print(node.lexeme)
          IDCurrent = verificarExistenciaEnPila(
              node.children[-1].children[-1].lexeme, scopeCurrent)
          if (IDCurrent == False):
            print("\nError Semantico(ES-05-2): La Variable '" +
                  node.children[-1].children[-1].lexeme +
                  "' no esta definida en el scope: " + scopeCurrent)
            exit(1)
          else:
            print("LEXEMEEEEE1", node.children[-1].children[-1].lexeme)
            print("TIPOOOOOOOOOOOO1", IDCurrent.type)
            actualType = [IDCurrent.type]
            verificarTiposCalculator(node, actualType)
            node.type = actualType[-1]
      else:
        print("LEXEMEEEEE", node.children[-1].children[-1].lexeme)
        print("TIPOOOOOOOOOOOO", node.children[-1].children[-1].type)
        actualType = [node.children[-1].children[-1].type]
        verificarTiposCalculator(node, actualType)
        node.type = actualType[-1]
      # VERIFICACION DE TIPOS
      if node.father.symbol == 'ASSIGN_VAR':
        if definirTipo(node.type,
                       node.father.father.children[-2].type) != None:
          print("HAY COMPATIBILIDAD DE DATOS")
          #aqui falta hacer la asignacion de valores
        else:
          print("\nError Semantico(ES-CAL): No hay compatibilidad de datos FUNC")
          exit(1)
      elif node.father.symbol == 'FUNC_OR_ASSIGN':
        if definirTipo(node.type,
                       idCurr.type) != None:
          print("HAY COMPATIBILIDAD DE DATOS")
          #aqui falta hacer la asignacion de valores
        else:
          print("CALC",
                definirTipo(node.type, idCurr.type))
          print(
              "\nError Semantico(ES-CAL-2): No hay compatibilidad de datos FUNC"
          )
          exit(1)

    for child in reversed(node.children):
      reconocerVariablesFunc(child, node.symbol)


reconocerFunciones(rootP)
archivo.write("digraph G {\n")
imprimir_arbol_preorden_inverso(rootP)
archivo.write("}\n")
archivo.close()
separador = "-" * 60
print(separador)
print("Test Analizador Semantico: Passed :)")
printStack()
print(separador)
