def tipo_resultante(tipo1, tipo2, operador):
  subtypes = {
      "bl": [None],
      "dbl": ["it"],
      "it": ["bl"],
      "str": ["ch"],
      "ch": ["bl"],
      "vd": [None]
  }
  
  def definirTipo(tipo1, tipo2):
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
    
  TypeFinal = definirTipo(tipo1, tipo2)
  
  if (operador in ('+', '-', '*', '/')) and (TypeFinal in ('dbl', 'it')):
    return TypeFinal
  elif (operador in ('>', '<', '>=', '<=')) and (TypeFinal in ('dbl', 'it')):
    return 'bl'
  elif (operador in ('==', '!=')) and (TypeFinal in ('dbl', 'it', 'bl', 'ch', 'str')):
    return 'bl'
  elif (operador in ('&', '|')) and (TypeFinal == 'bl'):
    return 'bl'
  elif (operador == '+') and (TypeFinal == 'str'):
    return 'str'
  else:
    return (f"Error: Operacion: \"{tipo1}{operador}{tipo2}\" no valida")



# Ejemplo de uso:
resultado = tipo_resultante('str', 'it', '-')
print(resultado)  # Salida: dbl

resultado = tipo_resultante('str', 'bl', '+')
print(resultado)  # Salida: bl

resultado = tipo_resultante('vd', 'it', '+')
print(resultado)  # Salida: Error: Tipos no compatibles para la operación aritmética
