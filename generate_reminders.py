import os
import numpy as np
import pandas as pd
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
tareas_path = os.path.join(dir_path, 'tareas.csv')
ayudantias_path = os.path.join(dir_path, 'ayudantias.csv')
config_path = os.path.join(dir_path, 'config.json')
reminder_path = os.path.join(dir_path, 'reminders.json')

with open(config_path, 'r') as f:
    config = json.load(f)

tareas_df = pd.read_csv(tareas_path).fillna('')
ayudantias_df = pd.read_csv(ayudantias_path).fillna('')

reminders_dict = {}

for _, tarea in tareas_df.iterrows():
    fecha_publicacion = tarea['Publicacion'].split('-')
    fecha_publicacion = "-".join([fecha_publicacion[2], fecha_publicacion[1], fecha_publicacion[0]])

    encargados = [tarea[f"Encargado {i}"] for i in range(1, 5) if tarea[f"Encargado {i}"]]
    encargados = ", ".join(encargados)

    reminders_dict.setdefault(tarea['Comienzo'], []).append({"message": f"{encargados}\n\nDesde hoy comienza el desarrollo de la Tarea {tarea['Tarea']} con publicacion el dia {fecha_publicacion}",
                                             "chat_id": config["AYUDANTES_CHAT_ID"]})
    
    reminders_dict.setdefault(tarea['Comienzo'], []).append({"message": f"Recuerda crear el grupo de telegram para la Tarea {tarea['Tarea']} con los siguientes ayudantes:\n\n{encargados}",
                                             "chat_id": config["AYUDANTE_JEFE_CHAT_ID"]})

    headers = ["Update 1", "Update 2"]

    for i in range(len(headers)):
        reminders_dict.setdefault(tarea[headers[i]], []).append({"message": f"En {2 - i} semana(s) debera estar lista la Tarea {tarea['Tarea']}. Recuerda agendar una revision de progreso",
                                                                        "chat_id": config["AYUDANTE_JEFE_CHAT_ID"]})

    reminders_dict.setdefault(tarea['Termino'], []).append({"message": f"Recuerda agendar la reunion de explicacion previo a la publicacion de la Tarea {tarea['Tarea']}",
                                                                    "chat_id": config["AYUDANTE_JEFE_CHAT_ID"]})
    
    reminders_dict.setdefault(tarea['Publicacion'], []).append({"message": f"Hoy se publica la Tarea {tarea['Tarea']}",
                                                                    "chat_id": config["AYUDANTES_CHAT_ID"]})
    
    reminders_dict.setdefault(tarea['Publicacion'], []).append({"message": f"Recuerda cambiar a los ayudantes en el chat de Issues a aquellos asignados a la Tarea {tarea['Tarea']}:\n\n{encargados}",
                                                                    "chat_id": config["AYUDANTE_JEFE_CHAT_ID"]})

for _, ayudantia in ayudantias_df.iterrows():
    fecha_ayudantia = ayudantia['Ayudantia'].split('-')
    fecha_ayudantia = "-".join([fecha_ayudantia[2], fecha_ayudantia[1], fecha_ayudantia[0]])

    fecha_control = ayudantia['Control'].split('-')
    fecha_control = "-".join([fecha_control[2], fecha_control[1], fecha_control[0]])

    encargados = [ayudantia[f"Encargado {i}"] for i in range(1, 3) if ayudantia[f"Encargado {i}"]]
    encargados = ", ".join(encargados)

    reminders_dict.setdefault(ayudantia['Reminder Ayudantia'], []).append({"message": f"{encargados}\n\nRecuerden armar la ayudantia y control correspondiente sobre {ayudantia['Titulo']} para los dias {fecha_ayudantia} y {fecha_control} respectivamente.",
                                                                    "chat_id": config["AYUDANTES_CHAT_ID"]})
    
    reminders_dict.setdefault(ayudantia['Reminder Ayudantia'], []).append({"message": f"Recuerda crear el grupo de telegram para la Ayudantia sobre {ayudantia['Titulo']} con los siguientes ayudantes:\n\n{encargados}",
                                                                    "chat_id": config["AYUDANTE_JEFE_CHAT_ID"]})
    
    reminders_dict.setdefault(ayudantia['Ayudantia'], []).append({"message": f"{encargados}\n\nRecuerden que hoy deben hacer la ayudantia sobre {ayudantia['Titulo']} y tener el control respectivo listo.",
                                                                    "chat_id": config["AYUDANTES_CHAT_ID"]})
    
    reminders_dict.setdefault(ayudantia['Ayudantia'], []).append({"message": f"Recuerda subir el control sobre {ayudantia['Titulo']} a Canvas.",
                                                                    "chat_id": config["AYUDANTE_JEFE_CHAT_ID"]})
    
json_object = json.dumps(reminders_dict, indent = 4)
with open(reminder_path, "w") as outfile:
    outfile.write(json_object)
    