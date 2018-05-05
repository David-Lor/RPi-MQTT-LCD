
# CONTROLADOR DE LCD POR MQTT CON COLAS
# Partes involucradas:
#   * mqttclient.py - lee el topic lcd, decodifica los mensajes json y se los manda a lcd_manager
#   * lcdmanager.py - gestiona la cola y según las prioridades y demás, imprime en pantalla con lcd_i2c
#   * lcd_i2c.py    - el controlador directo del lcd
#
# Estructura JSON (Payload):
# {
#     "lineA" : "mensaje linea 1", # "lineA" : "**clearscreen**" para limpiar pantalla (sólo mandar este campo)
#     "lineB" : "mensaje linea 2", # si no hay mensaje para una linea, "". Si hay que rotar, array
#     "priority" : 100, #prioridad (mas alta=mayor prioridad | 100=default) opcional
#     "min_time" : 0, #tiempo minimo que debe mostrarse (0=sin tiempo, default) opcional
#     "max_time" : 0, #tras este tiempo, el mensaje se borrará (0=sin tiempo, default) opcional
#     "rotate_freq" : 0.5, #tiempo de rotaciones (default=0.5) opcional
#     "autoclear" : 1 #autoclear on destroy (default=0) opcional
# }
#   Valores "opcionales" se ponen a su default en mqttclient
#   Para no actuar sobre una línea, usar el comodín "**ignore**" (se comprueba en lcd_i2c.py > lcd_print)
#   Para limpiar toda la pantalla usar el comodín "**clearscreen**"
#   (todos los comodines en "lineA")
#   Para limpiar una línea se puede enviar string vacío ""
# Ejemplo 1: {"lineA":"hola", "lineB":"hamijos"}
# Ejemplo 2: {"lineA":["hola", "holita"], "lineB":"hamijos"}
# Ejemplo 3: {"lineA":"hola", "lineB":["poios", "hermanous"]}
# Ejemplo 4: {"lineA":["hola", "hamijos"], "lineB":["poios", "hermanous"]}
# Ejemplo 5: {"lineA":"hola", "lineB":"hamijos", "max_time":2}
# Ejemplo 6: {"lineA":"hola", "lineB":"hamijos", "min_time":10, "priority":1} #COMPROBAR al implementar min_time
# Ejemplo 7: {"lineA":"vamo a", "lineB":"limpiarlo", "autoclear":1}
# Ejemplo 8: {"lineA":["hola", "hamijos"], "lineB":["poios", "hermanous"], "rotate_freq":0.212345, "max_time":5}
# Ejemplo 9: {"lineA":"**clearscreen"}
# Ejemplo 10: {"lineA":"Hola", "lineB":"**ignore**"}
# Ejemplo 11: {"lineB":"Hola", "lineA":"**ignore**"}

from mqttclient import loop

loop()
