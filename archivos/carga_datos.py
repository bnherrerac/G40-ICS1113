tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
rutas = ["Norte", "Centro", "Sur"]
paises = ["Chile", "Argentina"]

def alimentos(tipos):
    archivo = open("archivos/alimentos.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    alimentos = {}

    for tipo in tipos:
        alimentos[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                alimentos[tipo].append(linea[1])

    # print(alimentos)

    #Cantidad de alimentos en cada tipo
    cant_por_tipo = []
    for tipo in tipos:
        cant_por_tipo.append(len(alimentos.get(tipo)))
    # print(cant_por_tipo)

    total = sum(cant_por_tipo)
    # print(total)
    return alimentos, cant_por_tipo, total

# alimentos(tipos)


# CFB_i [CLP/semana]
# Costo fijo de almacenamiento de alimentos de tipo i (el total de una bodega)

def costo_fijo_almacenamiento():
    archivo = open("archivos/costo_fijo_almacenamiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_fijo_almacenamiento = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # costo_fijo_almacenamiento.append(linea)
        costo_fijo_almacenamiento[linea[0]] = linea[1]
    # print(costo_fijo_almacenamiento)
    return(costo_fijo_almacenamiento)

# tipos = ["Hortofruticola", "Congelado", "Refrigerado"]
# costo_fijo_almacenamiento()


# VB_i [m^3]
# Volumen máximo que puede almacenar una bodega de alimentos tipo i

def volumen_bodegas():
    archivo = open("archivos/volumen_bodegas.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    volumen_bodegas = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # volumen_bodegas.append(linea)
        volumen_bodegas[linea[0]] = linea[1]
    # print(volumen_bodegas)
    return(volumen_bodegas)

# volumen_bodegas()


# CTR_i [CLP/camión*semana]
# Costo adicional asociado al acondicionamiento de un camión de la categoría i por una semana

def costo_adicional_camiones():
    archivo = open("archivos/costo_adicional_camiones.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_adicional_camiones = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # costo_adicional_camiones.append(linea)
        costo_adicional_camiones[linea[0]] = linea[1]
    # print(costo_adicional_camiones)
    return(costo_adicional_camiones)

# costo_adicional_camiones()


# CAL_i [$/m^3*semana]
# Costo por almacenar un m^3 de alimento de tipo i por una semana

def costo_unitario_almacenamiento():
    archivo = open("archivos/costo_unitario_almacenamiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_unitario_almacenamiento = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # costo_unitario_almacenamiento.append(linea)
        costo_unitario_almacenamiento[linea[0]] = linea[1]
    # print(costo_unitario_almacenamiento)
    return(costo_unitario_almacenamiento)

# costo_unitario_almacenamiento()


# q_a,i [unidades]
# Cantidad de unidades iniciales de alimento a de tipo i para satisfacer 
# la demanda inicial.

def stock_inicial(tipos):
    archivo = open("archivos/stock_inicial.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    stock_inicial = {}
    
    for tipo in tipos:
        stock_inicial[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                stock_inicial[tipo].append({linea[1]:linea[2]})

    for tipo in tipos:
        lista = stock_inicial[tipo]
        stock_inicial[tipo] = {k:v for elem in lista for k,v in elem.items()}
    # print(stock_inicial)
    return(stock_inicial)

# stock_inicial(tipos)    


# d_t;a,i [unidades/semana]
# Demanda del alimento a del tipo i en el tiempo t

def demanda(tipos):
    archivo = open("archivos/demanda.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    demanda = {}
    
    for tipo in tipos:
        demanda[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                demanda[tipo].append({linea[1]:linea[2]})

    for tipo in tipos:
        lista = demanda[tipo]
        demanda[tipo] = {k:v for elem in lista for k,v in elem.items()}
    # print(demanda)
    return(demanda)

demanda(tipos)    


# P_a,i [kg/unidad]
# Peso promedio de unidad de alimento a de tipo i

def peso_promedio(tipos):
    archivo = open("archivos/peso_promedio.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    peso_promedio = {}
    
    for tipo in tipos:
        peso_promedio[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(";")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                peso_promedio[tipo].append({linea[1]:linea[2]})

    for tipo in tipos:
        lista = peso_promedio[tipo]
        peso_promedio[tipo] = {k:v for elem in lista for k,v in elem.items()}
    # print(peso_promedio)
    return(peso_promedio)

# peso_promedio(tipos)

# V_a,i [m^3/unidad]
# Volumen promedio de una unidad de alimento a de la categoría i

def volumen_promedio(tipos):
    archivo = open("archivos/volumen_promedio.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    volumen_promedio = {}
    
    for tipo in tipos:
        volumen_promedio[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                volumen_promedio[tipo].append({linea[1]:linea[2]})

    for tipo in tipos:
        lista = volumen_promedio[tipo]
        volumen_promedio[tipo] = {k:v for elem in lista for k,v in elem.items()}
    # print(volumen_promedio)
    return(volumen_promedio)

# volumen_promedio(tipos)

# H_a,i [$/unidad]
# Costo asociado a desechar unidad de alimento a de tipo i

def costo_vencimiento(tipos):
    archivo = open("archivos/costo_vencimiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_vencimiento = {}
    
    for tipo in tipos:
        costo_vencimiento[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                costo_vencimiento[tipo].append({linea[1]:linea[2]})

    for tipo in tipos:
        lista = costo_vencimiento[tipo]
        costo_vencimiento[tipo] = {k:v for elem in lista for k,v in elem.items()}
    # print(costo_vencimiento)
    return(costo_vencimiento)

# costo_vencimiento(tipos)


# l_r,p [km]
# Distancia total que recorre un camión en el país p en la ruta r

def distancia_por_pais(rutas):
    archivo = open("archivos/distancia_por_pais.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    distancia_por_pais = {}
    
    for ruta in rutas:
        distancia_por_pais[ruta] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for ruta in rutas:
            if linea[0] == ruta:
                distancia_por_pais[ruta].append({linea[1]:linea[2]})

    for ruta in rutas:
        lista = distancia_por_pais[ruta]
        distancia_por_pais[ruta] = {k:v for elem in lista for k,v in elem.items()}
    # print(distancia_por_pais)
    return(distancia_por_pais)

# distancia_por_pais(rutas)


# PC_p [$/km]
# Costo por kilómetro del combustible en el país p

def costo_combustible():
    archivo = open("archivos/costo_combustible.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_combustible = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # costo_combustible.append(linea)
        costo_combustible[linea[0]] = linea[1]
    # print(costo_combustible)
    return(costo_combustible)


# costo_combustible()


# PT_r [$]
# Costo total (peaje + aduana) de la ruta r

def costo_ruta():
    archivo = open("archivos/costo_ruta.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_ruta = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # costo_ruta.append(linea)
        costo_ruta[linea[0]] = linea[1]
    # print(costo_ruta)
    return(costo_ruta)


# costo_ruta()


# S_r [$/camión]
# Sueldo que percibe el conductor de un camión por conducir
# en la ruta r.

def sueldo():
    archivo = open("archivos/sueldo.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    sueldo = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # sueldo.append(linea)
        sueldo[linea[0]] = linea[1]
    # print(sueldo)
    return(sueldo)

# sueldo()


# M_r [$/camión]
# Costo de mantención de un camión al conducir por la ruta r

def costo_mantencion():
    archivo = open("archivos/costo_mantencion.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    costo_mantencion = {}
    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        # costo_mantencion.append(linea)
        costo_mantencion[linea[0]] = linea[1]
    # print(costo_mantencion)
    return(costo_mantencion)

# costo_mantencion()


# v_a,i [$/camión]
# Tiempo en semanas de vencimiento del alimento a de tipo i

def vencimiento(tipos):
    archivo = open("archivos/vencimiento.csv", "r")
    datos = archivo.readlines()
    archivo.close()
    vencimiento = {}
    
    for tipo in tipos:
        vencimiento[tipo] = []

    for i in range(1,len(datos)):
        linea = datos[i].split("\n")[0].split(",")
        # print(linea)
        for tipo in tipos:
            if linea[0] == tipo:
                vencimiento[tipo].append({linea[1]:linea[2]})

    for tipo in tipos:
        lista = vencimiento[tipo]
        vencimiento[tipo] = {k:v for elem in lista for k,v in elem.items()}
    print("Vencimiento =", vencimiento)
    return(vencimiento)


vencimiento(tipos)