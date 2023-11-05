import pandas as pd
import alex


class node_stack:

  def __init__(self, symbol, lexeme):
    global count
    self.symbol = symbol
    self.lexeme = lexeme
    self.id = count + 1
    count += 1


class node_tree:

  def __init__(self, id, symbol, lexeme):
    self.id = id
    self.symbol = symbol
    self.lexeme = lexeme
    self.children = []
    self.father = None


def buscar_nodo_por_id(root, target_id):
  if root.id == target_id:
    return root
  for child in root.children:
    result = buscar_nodo_por_id(child, target_id)
    if result is not None:
      return result
  return None


tabla = pd.read_csv("gramaticaFinal.csv", index_col=0)
count = 0
stack = []

# Inicializa la pila
symbol_E = node_stack('STAR', None)
symbol_dollar = node_stack('$', None)
stack.append(symbol_dollar)
stack.append(symbol_E)

# Inicializa el árbol
rootp = node_tree(symbol_E.id, symbol_E.symbol, symbol_E.lexeme)

input_data4 = alex.alex()


def asin():
  while stack[-1].symbol != '$':

    symbol_stack = stack[-1].symbol
    symbol_input = input_data4[0]["symbol"]
    if symbol_stack == symbol_input:
      nodeCurrent = buscar_nodo_por_id(rootp, stack[-1].id)
      nodeCurrent.lexeme = input_data4[0]["lexeme"]
      stack.pop()
      input_data4.pop(0)
    else:
      if (symbol_stack not in tabla.index
          or symbol_input not in tabla.columns):
        print("Error de Sintantico(ESI-01): \'", input_data4[0]["lexeme"],
              "\' en la linea", input_data4[0]["nroline"], "en la columna ",
              input_data4[0]["col"])
        exit(1)
      production = tabla.loc[symbol_stack, symbol_input]
      #print("La produccion es: ", production)
      if pd.isna(production):
        print("Error de Sintantico(ESI-02): \'", input_data4[0]["lexeme"],
              "\' en la linea", input_data4[0]["nroline"], "en la columna ",
              input_data4[0]["col"])
        exit(1)
      elif production != 'e':
        node_f = stack.pop()
        for symbol in reversed(production.split()):
          node_stackX = node_stack(symbol, None)
          stack.append(node_stackX)
          node_treeX = node_tree(node_stackX.id, node_stackX.symbol,
                                 node_stackX.lexeme)
          node_father = buscar_nodo_por_id(rootp, node_f.id)
          node_father.children.append(node_treeX)
          node_treeX.father = node_father
      else:
        node_f = stack.pop()
        node_stackX = node_stack('e', None)
        node_treeX = node_tree(node_stackX.id, node_stackX.symbol,
                               node_stackX.lexeme)
        node_father = buscar_nodo_por_id(rootp, node_f.id)
        node_father.children.append(node_treeX)
        node_treeX.father = node_father

  nombre_archivo = "arbolSintatico.txt"
  archivo = open(nombre_archivo, "w")
  padres_impresos = []

  def imprimir_arbol_preorden_inverso(node, padre=None):
    if node is not None:
      for child in reversed(node.children):
        imprimir_arbol_preorden_inverso(child, node)
      if padre is not None:
        if len(node.children) == 0:
          archivo.write(
              f"{node.id} [style = filled fillcolor= yellow label = <{node.symbol}<BR/>'{node.lexeme}'>]\n"
          )
        if padre.id not in padres_impresos:
          archivo.write(
              f"{padre.id} [style = filled fillcolor= gray label = <{padre.symbol}<BR/>'{padre.lexeme}'>]\n"
          )
          padres_impresos.append(padre.id)
        archivo.write(f"{padre.id} -> {node.id}\n")

  if stack[-1].symbol == "$":
    print("Test Analizador Sintactico: Passed :)")
    #print("El Arbol es: ")
    #print("digraph G {")
    archivo.write("digraph G {\n")
    imprimir_arbol_preorden_inverso(rootp)
    #print("}")
    archivo.write("}\n")
    archivo.close()
    print("El arbol sitactico ha sido generado en:", nombre_archivo)
  return rootp
