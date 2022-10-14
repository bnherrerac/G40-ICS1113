# CTR_i [CLP/camión*semana]
# Costo adicional asociado al acondicionamiento de un camión de la categoría i por una semana

def costo_adicional_camiones():
    archivo = open("archivos/costo_adicional_camiones.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_adicional_camiones = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_adicional_camiones.append(linea)

    return(costo_adicional_camiones)

# costo_adicional_camiones()

# CFB_i [CLP/semana]

def costo_fijo_almacenamiento():
    archivo = open("archivos/costo_fijo_almacenamiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_fijo_almacenamiento = []
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_fijo_almacenamiento.append(linea)

    return(costo_fijo_almacenamiento)

tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
costo_fijo_almacenamiento(tipos)