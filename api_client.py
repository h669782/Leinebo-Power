# api_client.py
import requests
from datetime import datetime

def fetch_data(config):
    try:
        headers = {'Authorization': config['Credentials']['authorization']}
        url = config['API']['url']
            
        now = datetime.now()
        days_passed = now.day 
            
        query = f'''
        {{
            viewer {{
                homes {{
                    consumption(resolution: DAILY, last: {days_passed}) {{
                        nodes {{
                            from
                            to
                            consumption
                            cost
                        }}
                    }}
                }}
            }}
        }}
        '''
        response = requests.post(url, json={'query': query}, headers=headers)
        response_data = response.json()
        if 'errors' in response_data:
            print("Det oppstod en feil i API-forespørselen.")
            return None
        print("Rådata fra API:", response.json())
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"Autorasjonsnøkkelen er feil: {e}")
        return None

# api_client.py

def fetch_hourly_price_data(config):
    headers = {'Authorization': config['Credentials']['Authorization']}
    url = config['API']['URL']

    query = '''
    {
        viewer {
            homes {
                currentSubscription {
                    priceInfo {
                        today {
                            total
                            startsAt
                            level
                        }
                    }
                }
            }
        }
    }
    '''
    try:
        response = requests.post(url, json={'query': query}, headers=headers)
        response_data = response.json()
        if 'errors' in response_data:
            print(f"Feil: {response_data['errors'][0]['message']}")
            return False

        hourly_price_data = response_data['data']['viewer']['homes'][0]['currentSubscription']['priceInfo']['today']

        times = [datetime.strptime(entry['startsAt'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%H') for entry in hourly_price_data]
        prices = [entry['total'] for entry in hourly_price_data]

        return {
            'times': times,
            'prices': prices,
        }

    except requests.exceptions.RequestException as e:
        print(f"Nettverksfeil: {e}")
        return None
    except Exception as e:
        print(f"En annen feil oppsto: {e}")
        return None
    

def fetch_monthly_data(config):
    try:
        headers = {'Authorization': config['Credentials']['authorization']}
        url = config['API']['url']

        # GraphQL-spørring for å hente forbruk og kostnad for de siste 12 månedene
        query = '''
        {
            viewer {
                homes {
                    consumption(resolution: MONTHLY, last: 12) {
                        nodes {
                            from
                            to
                            consumption
                            cost
                        }
                    }
                }
            }
        }
        '''

        response = requests.post(url, json={'query': query}, headers=headers)
        response_data = response.json()
        if 'errors' in response_data:
            print("Det oppstod en feil i API-forespørselen.")
            return None
        print("Månedlig data fra API:", response_data)
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"Autorasjonsnøkkelen er feil: {e}")
        return None
