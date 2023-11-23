# ------------------------------------------------------------
# calclex.py
# @Author(C): Carlos Mijail Mamani Anccasi
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply.lex as lex

# r'atring' -> r significa que la cadena es tradada sin caracteres de escape,
# es decir r'\n' seria un \ seguido de n (no se interpretaria como salto de linea)

# List of token names.   This is always required
reserved = {
    'run': 'MAIN',
    'it': 'TYPE_INT',
    'str': 'TYPE_STR',
    'dbl': 'TYPE_DBL',
    'ch': 'TYPE_CH',
    'bl': 'TYPE_BL',
    'iut': 'INPUT',
    'out': 'OUPUT',
    'whl': 'WHILE',
    'fr': 'FOR',
    'if': 'IF',
    'vd': 'TYPE_VOID',
    'els': 'ELSE',
    'elf': 'ELSE_IF',
    'tru': 'BOOL',
    'fal': 'BOOL',
    'rtn': 'RETURN',
    'slt': 'ENDL'
}

tokens = [
    'DOUBLE', 'NUM', 'CHAR', 'LITERAL', 'ID', 'OPE_IGU', 'OPER_ASG', 'OPE_MUL',
    'OPE_DIV', 'OPE_SUM', 'OPE_RES', 'OPE_MEN', 'OPE_MAY', 'OPE_MEN_IGU',
    'OPE_MAY_IGU', 'OPE_OR', 'OPE_AND', 'OPE_DIF', 'COMENTARIO', 'PAR_RIGHT',
    'PAR_LEFT', 'LLA_RIGHT', 'LLA_LEFT', 'COMMA', 'P_COMMA'
] + list(reserved.values())

# Regular expression rules for simple tokens
t_OPE_SUM = r'\+'
t_OPE_RES = r'-'
t_OPE_MUL = r'\*'
t_OPE_DIV = r'/'
t_OPE_IGU = r'=='
t_OPER_ASG = r'\='
t_OPE_MEN_IGU = r'<='
t_OPE_MAY_IGU = r'>='
t_OPE_MEN = r'<'
t_OPE_MAY = r'>'
t_OPE_OR = r'\|'
t_OPE_AND = r'&'
t_OPE_DIF = r'!='
t_PAR_LEFT = r'\('
t_PAR_RIGHT = r'\)'
t_LLA_RIGHT = r'\}'
t_LLA_LEFT = r'\{'
t_COMMA = r','
t_P_COMMA = r';'


# A regular expression rule with some action code
def t_ID(t):
  r'[a-zA-Z]+ ( [a-zA-Z0-9]* )'
  t.type = reserved.get(t.value, 'ID')  # Check for reserved words
  return t


def t_DOUBLE(t):
  r'\d+\.\d*'
  t.value = float(t.value)  # guardamos el valor del lexema
  #print("se reconocio el numero")
  return t


def t_NUM(t):
  r'\d+'
  t.value = int(t.value)  # guardamos el valor del lexema
  #print("se reconocio el numero")
  return t


def t_CHAR(t):
  r"'.'"
  t.value = str(t.value[1])  # Elimina las comillas y obtiene el carácter
  return t


def t_LITERAL(t):
  r'"[^"]*"'
  t.value = str(t.value[1:-1])  # Elimina las comillas al principio y al final
  return t


def t_COMENTARIO(t):
  r'\#.*\#'
  pass
  '''t.value = t.value[1:-1]  # Elimina los símbolos # al principio y al final
  return t'''


# Define a rule so we can track line numbers
def t_newline(t):
  r'\n+'
  t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
  print("Error Lexico(EL-01): Caracter ilegal '%s'" % t.value[0],
        "en la linea", t.lineno, ", en la columna", t.lexpos)
  exit(1)
  #t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()


# Give the lexer some input
def alex():
  with open('test/run.cppl', 'r') as archivo:
    contenido = archivo.read()

  lexer.input(contenido)

  lista_tokens = []

  while True:
    tok = lexer.token()
    if not tok:
      break
    info_token = {
        "symbol": tok.type,
        "lexeme": tok.value,
        "nroline": tok.lineno,
        "col": tok.lexpos
    }
    lista_tokens.append(info_token)
  nuevo_token = {"symbol": "$", "lexeme": "$", "nroline": 0, "col": 0}
  lista_tokens.append(nuevo_token)
  separador = "-" * 60
  for info_token in lista_tokens:
    print(info_token)
  print(separador)
  print("\t\t\t\t\tCOMPILADOR CPP-LITE")
  print(separador)
  print("Test Analizador Lexico: Passed :)")
  print(separador)
  return lista_tokens
  # Imprime la lista de diccionarios de tokens
  #for info_token in lista_tokens:
  #  print(info_token)
  #return lista_tokens
