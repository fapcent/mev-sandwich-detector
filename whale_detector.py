import os
import time
from web3 import Web3
from colorama import Fore, Style, init
from dotenv import load_dotenv

init(autoreset=True)
load_dotenv()

# --- 1. CONFIGURATION ---
# Mettez votre URL Alchemy ici ou dans un fichier .env
ALCHEMY_URL = os.getenv('ALCHEMY_URL', 'VOTRE_URL_ALCHEMY_ICI')

# Adresse du routeur Uniswap V2 (Le contrat qui gère les échanges)
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

# Seuil pour considérer une transaction comme "Whale" (en ETH)
WHALE_THRESHOLD_ETH = 5.0 

# --- 2. CONNEXION ---
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

if not w3.is_connected():
    print(f"{Fore.RED}❌ Erreur : Impossible de se connecter à Ethereum via Alchemy.")
    exit()
else:
    print(f"{Fore.GREEN}✅ Connecté à Ethereum Mainnet (Dernier bloc: {w3.eth.block_number})")
    print(f"{Fore.CYAN}👀 Surveillance des échanges Uniswap (> {WHALE_THRESHOLD_ETH} ETH)...")

def calculate_market_impact(eth_amount):
    """
    Fonction Quant : Estime l'impact sur le prix.
    Modèle simplifié : Impact = Racine carrée du montant (Heuristic)
    Dans un vrai hedge fund, on utiliserait la liquidité réelle du pool.
    """
    # Simulation d'impact
    impact_percent = (eth_amount ** 0.5) * 0.1 
    return impact_percent

def handle_new_block(block_filter):
    try:
        # Récupère les nouveaux blocs
        new_entries = block_filter.get_new_entries()
        
        for block_hash in new_entries:
            try:
                # On télécharge le bloc entier avec toutes ses transactions
                block = w3.eth.get_block(block_hash, full_transactions=True)
                print(f"\n📦 Analyse du Bloc #{block['number']} ({len(block['transactions'])} txs)...")
                
                for tx in block['transactions']:
                    process_transaction(tx)
                    
            except Exception as e:
                print(f"Erreur lecture bloc: {e}")
                
    except Exception as e:
        pass

def process_transaction(tx):
    # On regarde seulement les transactions qui vont vers Uniswap
    if tx['to'] == UNISWAP_V2_ROUTER:
        
        # Convertir la valeur de Wei (entier) vers ETH (décimal)
        value_eth = float(w3.from_wei(tx['value'], 'ether'))
        
        # Si c'est une grosse transaction
        if value_eth > WHALE_THRESHOLD_ETH:
            impact = calculate_market_impact(value_eth)
            
            # Affichage de l'analyse
            print(f"{Fore.YELLOW}🐋 WHALE DETECTED sur Uniswap !")
            print(f"   ├─ Hash : {tx['hash'].hex()}")
            print(f"   ├─ De   : {tx['from']}")
            print(f"   ├─ Valeur : {Fore.GREEN}{value_eth:.2f} ETH {Style.RESET_ALL}(~${value_eth * 3500:.0f})")
            print(f"   ├─ Gas Price : {w3.from_wei(tx['gasPrice'], 'gwei'):.0f} Gwei")
            print(f"   └─ Impact Prix Estimé : {Fore.RED}+{impact:.2f}%")
            
            if impact > 0.5:
                print(f"{Fore.MAGENTA}   🚨 OPPORTUNITÉ MEV (Sandwich) DÉTECTÉE !")
                print(f"      Un attaquant pourrait front-run cette transaction pour {impact:.2f}% de profit.")

# --- 3. BOUCLE PRINCIPALE ---
def main():
    # Création d'un filtre pour écouter les nouveaux blocs
    block_filter = w3.eth.filter('latest')
    
    while True:
        handle_new_block(block_filter)
        time.sleep(2)

if __name__ == "__main__":
    main()