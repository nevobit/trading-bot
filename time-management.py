from datetime import datetime, time
def is_new_york_trading_time(self):
        # Obtener la hora actual en Nueva York
        current_time = datetime.now(self.ny_tz).time()
        
        # Definir el rango de tiempo de operación (7am a 1pm)
        start_time = time(7, 0)  # 7am
        end_time = time(13, 0)   # 1pm

        # Verificar si la hora actual está dentro del rango de operación
        if start_time <= current_time <= end_time:
            return True
        else:
            return False