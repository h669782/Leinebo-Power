# visualization.py
import matplotlib.pyplot as plt

def plot_data(processed_data):
    if not processed_data:
        print("Ingen data å vise.")
        return

    dates = processed_data['dates']
    consumption = processed_data['consumption']
    cost = processed_data['cost']

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('Dato')
    ax1.set_ylabel('Forbruk (kWh)', color=color)
    ax1.plot(dates, consumption, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # Opprette en annen akse som deler samme x-akse
    color = 'tab:blue'
    ax2.set_ylabel('Kostnad', color=color)  
    ax2.plot(dates, cost, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # For å sikre at layouten ikke overlapper
    plt.show()
