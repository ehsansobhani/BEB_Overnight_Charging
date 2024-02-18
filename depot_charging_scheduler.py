import math
import time
import threading
import pandas as pd


# Print the DataFrame
# print(df)

# class Bus:
#    def __init__(self, id, battery_size, arrival_soc, arrival_time):
#        self.id = id
#        self.battery_size = battery_size
#        self.arrival_soc = arrival_soc
#        self.arrival_time = arrival_time
#        self.current_soc = arrival_soc
#        self.charge_time = math.ceil((battery_size - arrival_soc) / 150)
#        self.remaining_charge_time = self.charge_time

class Bus:
   def __init__(self, id, battery_size, arrival_soc, arrival_time):
       self.id = id
       self.battery_size = battery_size
       self.arrival_soc = arrival_soc
       self.arrival_time = arrival_time

       self.current_soc = arrival_soc
       self.charge_time = math.ceil((battery_size - arrival_soc) / 175)
       self.remaining_charge_time = self.charge_time
       self.charging_sessions = []  # List to store tuples of (start_charging_time, end_charging_time)
       
class ChargingScheduler:
    def __init__(self, quantum, update_progress_callback=None):
        self.quantum = quantum
        self.buses = []
        self.buses_for_time_rocord = []
        self.update_progress_callback = update_progress_callback

    def show_current_soc(self):
        while True:
            for bus in self.buses:
                print(f"Bus {bus.id} current SOC: {bus.current_soc}")
            time.sleep(10)


    def add_bus(self, bus):
        self.buses.append(bus)


    
    


    def schedule(self):
        i = 0
        while self.buses:
            i = i + 1
            # Sort buses by remaining charge time in descending order
            self.buses.sort(key=lambda bus: bus.remaining_charge_time, reverse=True)
            # Perform two charging operations
            for _ in range(15):
                if not self.buses:
                    break
                # Get the bus with the highest priority
                bus = self.buses[0]
                if bus.remaining_charge_time > (self.quantum ):
                    if not bus.charging_sessions or bus.charging_sessions[-1][1] is not None:
                        bus.charging_sessions.append((time.time(),time.time()+ self.quantum))
                    bus.remaining_charge_time -= self.quantum
                    bus.current_soc += self.quantum * 175
                    print(f"Bus {bus.id} charged for {self.quantum} hours. Remaining charge time: {bus.remaining_charge_time} hours.")
                    # Move the bus to the end of the list
                    self.buses.append(self.buses.pop(0))
                else:
                    if not bus.charging_sessions or bus.charging_sessions[-1][1] is not None:
                        bus.charging_sessions.append((time.time(), time.time()+bus.remaining_charge_time))
                    bus.current_soc += bus.remaining_charge_time * 175
                    print(f"Bus {bus.id} fully charged.")
                    self.buses.remove(bus)
                    self.buses_for_time_rocord.append(bus)
            time.sleep(5)
            print(f"{self.quantum*i} hour(s) //////////////////////////////////////////////////////////////")
        all_sessions = []
        # After scheduling is complete, print the charging sessions for each bus
        for bus in self.buses_for_time_rocord:
            print(f"Bus {bus.id} charging sessions:")
            j = 0
            for session in bus.charging_sessions:
                
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session[0]))
                end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session[1])) if session[1] else "In progress"
                print(f"  Start: {start_time}, End: {end_time}")
                all_sessions.append({
            'Bus ID': bus.id,
            'Start Time': start_time,
            'End Time': end_time
        })
                j = j + 1
                 # Convert the list to a DataFrame
        all_charging_sessions = pd.DataFrame(all_sessions)

        # Save the DataFrame to an Excel file
        # all_charging_sessions.to_excel('E:/winter2024/depot_charging/charging_sessions.xlsx', index=False)

# Create scheduler with a quantum of 2 hours
scheduler = ChargingScheduler(0.2)





from tkinter import Tk, Canvas, Label


class SOCForm:
    def __init__(self, scheduler):
        self.root = Tk()
        self.scheduler = scheduler
        self.initUI()

    def initUI(self):
        for i, bus in enumerate(self.scheduler.buses):
            Label(self.root, text=f"Bus {bus.id}").grid(row=i, column=0)
            canvas = Canvas(self.root, width=100, height=20)
            canvas.grid(row=i, column=1)
            canvas.create_rectangle(0, 0, bus.current_soc / bus.battery_size * 100, 20, fill="blue")
            self.scheduler.buses[i].current_soc = canvas

    def update_soc(self):
        while True:
            for bus in self.scheduler.buses:
                # bus.current_soc.delete("all")
                bus.current_soc.create_rectangle(0, 0, bus.current_soc / bus.battery_size * 100, 20, fill="blue")

    def run(self):
        update_soc_thread = threading.Thread(target=self.update_soc)
        update_soc_thread.start()
        mainloop_thread = threading.Thread(target=self.root.mainloop)
        mainloop_thread.start()

# Create and run the form
# form = SOCForm(scheduler)
# form.run()




buses = []

def add_buses():
  # Add buses with different battery sizes and arrival SOCs
#   buses.extend([
#       Bus(1, 600, 250, 1200), # Battery size: 500, Arrival SOC: 250
#       Bus(2, 600, 150, 1260), # Battery size: 600, Arrival SOC: 200
#       Bus(3, 600, 300, 1300), # Battery size: 600, Arrival SOC: 300
#       Bus(4, 600, 220, 1100) # Battery size: 600, Arrival SOC: 220
#   ])
  # Read the Excel file
    df = pd.read_csv('E:/winter2024/depot_charging/route_bus_energy_consumption.csv')

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        # Extract the necessary data from the row
        id = row['Bus No.']
        # battery_size = row['minimum_required _battery_capacity']
        # battery_size = row['adjusted_battery']
        battery_size = row['Batt']
        
        # arrival_soc = row['arival_soc']
        arrival_soc = row['Ar_Soc']
        arrival_time = row['start_charging_over_night']

        # Create a new Bus object and add it to the scheduler
        bus = Bus(id, battery_size, arrival_soc, arrival_time)
        buses.append(bus)
   

    # Sort buses by arrival time
    buses.sort(key=lambda bus: bus.arrival_time)

#   # Add buses to scheduler
#   for bus in buses:
#       scheduler.add_bus(bus)
#       # Wait for an hour
#       time.sleep(60*60)

    for i in range (len(buses)):
        scheduler.add_bus(buses[i])
        # Wait for an hour
        if i+1 < len(buses):
            time.sleep(abs(buses[i+1].arrival_time - buses[i].arrival_time)/60)
   
     
def schedule_charging():
    # Schedule the charging
    scheduler.schedule()

# def save_charging_sessions_to_excel(buses, filename):
#     # Create a list to hold all the charging sessions
#     all_sessions = []

#     # Iterate over all buses
#     for bus in buses:
#         # Iterate over all charging sessions of the bus
#         for session in bus.charging_sessions:
#             # Append the session to the list
#             all_sessions.append({
#                 'Bus ID': bus.id,
#                 'Start Time': session[0],
#                 'End Time': session[1]
#             })

#     # Convert the list to a DataFrame
#     all_charging_sessions = pd.DataFrame(all_sessions)

#     # Save the DataFrame to an Excel file
#     all_charging_sessions.to_excel('E:/winter2024/depot_charging/charging_sessions.xlsx', index=False)



# Create threads for adding buses and scheduling charging
add_buses_thread = threading.Thread(target=add_buses)
schedule_charging_thread = threading.Thread(target=schedule_charging)
show_current_soc_thread = threading.Thread(target=scheduler.show_current_soc)

# Start the threads
add_buses_thread.start()
schedule_charging_thread.start()
# show_current_soc_thread.start()

# Wait for both threads to finish
add_buses_thread.join()
schedule_charging_thread.join()




















