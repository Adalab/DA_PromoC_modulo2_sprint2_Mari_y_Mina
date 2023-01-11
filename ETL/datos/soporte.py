# de nuevo, en este archivo deberemos poner todas las librerias que necesitamos para que se ejecute el código correctamente. 

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Extraccion: 
    # primero tenemos que crear el constructor con las variables globales que usaremos. Están son variables que podrán cambiar cada vez que llamemos a la clase. 
    def __init__(self, lat, lon, ciudad):

        # definimos cada una de las variables. Recordamos que tenemos que usar el método .self para definirlas y que la clase entienda que las podremos usar en otros métodos de la clase. 
        self.lat = lat
        self.lon = lon
        self.ciudad = ciudad

    # definimos nuestro primer método. El que nos hará la llamada a la API
    # Si comparamos, veremos que la función es exactamente igual a la que hicimos en la clase anterior, solo que con unos pequeños cambios. En este caso incluimos el parámetro self
    def llamada_API(self, producto):
        
        # producto es una variable nueva, por lo que lo primero que tenemos que hacer es definirla
        self.producto = producto
    
        # hacemos la llamada  a la API
        # Tendremos que poner el self delante de long y lat ya que son variables definidas en el constructor. El self podríamos decir que es como el camino de baldosas amarillas que indica al método de donde tiene que sacar esas variables
        url = f'http://www.7timer.info/bin/api.pl?lon=-{self.lon}&lat={self.lat}&product={producto}&output=json'

        response = requests.get(url=url)
        codigo_estado = response.status_code
        razon_estado = response.reason
        if codigo_estado == 200:
            print('La peticion se ha realizado correctamente, se ha devuelto el código de estado:',codigo_estado,' y como razón del código de estado: ',razon_estado)
        elif codigo_estado == 402:
            print('No se ha podido autorizar usario, se ha devuelto el código de estado:', codigo_estado,' y como razón del código de estado: ',razon_estado)
        elif codigo_estado == 404:
            print('Algo ha salido mal, el recurso no se ha encontrado,se ha devuelto el código de estado:', codigo_estado,' y como razón del código de estado: ',razon_estado)
        else:
            print('Algo inesperado ha ocurrido, se ha devuelto el código de estado:', codigo_estado,' y como razón del código de estado: ',razon_estado)

        # convertimos los resultados en un dataframe: 
        df = pd.DataFrame.from_dict(pd.json_normalize(response.json()['dataseries']))
        return df
    
    # definimos un nuevo método, el de limpiar los datos obtenidos de la llamada a la API para el producto civil. 
    def limpiar_civil(self, df): 

        # lo primero que tenemos que hacer es crear la columna de fecha en el dataframe nuevo 
        # En este caso será la fecha del día de hoy. 
        hoy = datetime.now()
        hoy = datetime.strftime(hoy, '%Y-%m-%d')

        # creamos la nueva columna
        df["fecha"] = hoy

        # de nuevo usamos el self para crear las nuevas columnas en función de los parámetros pasados al definir la clase. Recordamos, el caminito de baldosas amarillas.
        df["latitud"] = self.lat
        df["longitud"] = self.lon
        df["ciudad"] = self.ciudad
        return df
    
    
    # creamos una clase para limpiar el resultado de la llamada a la API para el producto astro
    def limpiar_astro(self, df):

        #seleccionamos solo las columnas que nos interesan
        df = df[["seeing", "transparency", "timepoint"]]

        # creamos la columna de fecha: 
        hoy = datetime.now()
        hoy = datetime.strftime(hoy, '%Y-%m-%d')
        df["fecha"] = hoy


        # insertamos las columnas de la localidad
    
        df["ciudad"] = self.ciudad

        return df
    
    # de nuevo, hacemos lo mismo que en la lección anterior. 
    def juntar_dfs(self, df_completo, df_civil, df_visibilidad): 

        df_hoy = pd.merge(df_civil , df_visibilidad , on=['fecha', "timepoint", "ciudad"], how = "right")
        print("El df de hoy es ", df_hoy.columns)
        print("-----------------------------------------")
        print("El df de completo es ", df_completo.columns)
        # lo primero que hacemos es concatenar los dataframes con la información general. df_completo y df_civil
        df_completo = pd.concat([df_completo, df_hoy], axis = 0)

        
        # guardamos los datos
        df_completo.to_pickle('../files/datos_actualizados.pkl')
        df_completo.to_csv('../files/datos_actualizados.csv')

        return df_completo
    
    

    def chequear_datos(self, df): 
    
        print("Las columnas son:", "\n")
        print(list(df.columns))
        print("-----------------------------------------")

        print("Los tipos de datos que tenemos son:", "\n")
        print(df.dtypes)
        print("-----------------------------------------")

        print("El porcentaje de nulos:", "\n")
        print((df.isnull().sum() / df.shape[0]) *  100)

    def limpiar_dataframe(self, df, lista_columnas = []): 

        #convertimos la fecha a datetime
        df["fecha"] = pd.to_datetime(df["fecha"])

        # reemplazamos los nulos de las columnas por la media
         # lista de columnas en las que queremos reemplazar los nulos
        df[lista_columnas]=df[lista_columnas].fillna(df.mean())

        
        # renombrar columnas
        
        df.rename(columns = {"ciudad_x": "ciudad"}, inplace = True)

        # quitar % 
        df["rh2m"] = df["rh2m"].replace(r"%", "", regex = True)

        # guardamos los datos una vez limpios
        df.to_pickle('../files/datos_actualizados.pkl')
        df.to_csv('../files/datos_actualizados.csv')

        return df
