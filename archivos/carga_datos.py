# CFB_i [CLP/semana]
# Costo fijo de almacenamiento de alimentos de tipo i (el total de una bodega)

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

# tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
# costo_fijo_almacenamiento()


# VB_i [m^3]
# Volumen máximo que puede almacenar una bodega de alimentos tipo i

def volumen_bodegas():
    archivo = open("archivos/volumen_bodegas.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    volumen_bodegas = []
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        volumen_bodegas.append(linea)

    return(volumen_bodegas)

#volumen_bodegas()


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


# CAL_i [$/m^3*semana]
# Costo por almacenar un m^3 de alimento de tipo i por una semana

def costo_unitario_almacenamiento():
    archivo = open("archivos/costo_unitario_almacenamiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_unitario_almacenamiento = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_unitario_almacenamiento.append(linea)
    return(costo_unitario_almacenamiento)

# costo_unitario_almacenamiento()


# q_a,i [unidades]
# Cantidad de unidades iniciales de alimento a de tipo i para satisfacer 
# la demanda inicial.

def stock_inicial():
    archivo = open("archivos/stock_inicial.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    stock_inicial = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        stock_inicial.append(linea)
    return(stock_inicial)

# stock_inicial()    


# d_t;a,i [unidades/semana]
# Demanda del alimento a del tipo i en el tiempo t

def demanda():
    archivo = open("archivos/demanda.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    demanda = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        demanda.append(linea)
    return(demanda)

# demanda()


# P_a,i [kg/unidad]
# Peso promedio de unidad de alimento a de tipo i

def peso_promedio():
    archivo = open("archivos/peso_promedio.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    peso_promedio = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        peso_promedio.append(linea)
    return(peso_promedio)

# peso_promedio()


# H_a,i [$/unidad]
# Costo asociado a desechar unidad de alimento a de tipo i

def costo_vencimiento():
    archivo = open("archivos/costo_vencimiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_vencimiento = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_vencimiento.append(linea)
    return(costo_vencimiento)

# costo_vencimiento()


# l_r,p [km]
# Distancia total que recorre un camión en el país p en la ruta r

def distancia_por_pais():
    archivo = open("archivos/distancia_por_pais.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    distancia_por_pais = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        distancia_por_pais.append(linea)
    return(distancia_por_pais)

# distancia_por_pais()


# PC_p [$/km]
# Costo por kilómetro del combustible en el país p

def costo_combustible():
    archivo = open("archivos/costo_combustible.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_combustible = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_combustible.append(linea)
    return(costo_combustible)

# costo_combustible()


# PT_r [$]
# Costo total (peaje + aduana) de la ruta r

def costo_ruta():
    archivo = open("archivos/costo_ruta.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_ruta = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_ruta.append(linea)
    return(costo_ruta)

# costo_ruta()


# S_r [$/camión]
# Sueldo que percibe el conductor de un camión por conducir
# en la ruta r.

def sueldo():
    archivo = open("archivos/sueldo.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    sueldo = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        sueldo.append(linea)
    return(sueldo)

# sueldo()


# M_r [$/camión]
# Costo de mantención de un camión al conducir por la ruta r

def costo_mantencion():
    archivo = open("archivos/costo_mantencion.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_mantencion = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_mantencion.append(linea)
    return(costo_mantencion)

# costo_mantencion()


# v_a,i [$/camión]
# Costo de mantención de un camión al conducir por la ruta r

def costo_mantencion():
    archivo = open("archivos/costo_mantencion.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_mantencion = []
    for i in range(1,len(datos)): # Se salta la primera línea
        linea = datos[i].split("\n")[0].split(",")
        print(linea)
        costo_mantencion.append(linea)
    return(costo_mantencion)

# costo_mantencion()