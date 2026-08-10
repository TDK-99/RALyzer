import json
from .schemas import RALInput, RALResult


# Algo for calculate the ral

def calcola_netto(ral_data: RALInput) -> RALResult:

    ral_lorda = ral_data.ral
    mensilita = ral_data.mensilita
    citta = ral_data.citta
    figli_sotto_21 = ral_data.figli_sotto_21
    figli_disabilita = ral_data.figli_disabilita
    addizionale_comunale = ral_data.addizionale_comunale
    addizionale_regionale = ral_data.addizionale_regionale


    from pathlib import Path
    config_path = Path(__file__).parent.parent / "data_ral_maker.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    # poi accedi con le chiavi
    inps_rate = config["inps"]["dipendente"]  
    ral_mensile_lorda= ral_lorda/mensilita
    INPS = ral_lorda*inps_rate


    # calcolo del irpeg su scaglioni json


    imponibile = ral_lorda - INPS

    irpef_lorda = 0
    precedente = 0

    for scaglione in config["irpef_scaglioni"]:
        limite = scaglione["fino_a"] if scaglione["fino_a"] is not None else float("inf")
        aliquota = scaglione["aliquota"]
        
        porzione = max(0, min(imponibile, limite) - precedente)
        irpef_lorda += porzione * aliquota
        
        precedente = limite

    # Detrazioni lavoro dipendente: importo fisso o formula decrescente
    # in base alla fascia di reddito. Si sottraggono dall'IRPEF lorda.

    det = config["detrazioni_lavoro_dipendente"]

    if imponibile <= det["fascia_1"]["fino_a"]:
        detrazioni = det["fascia_1"]["importo_fisso"]

    elif imponibile <= det["fascia_2"]["fino_a"]:
        detrazioni = det["fascia_2"]["base"] + det["fascia_2"]["extra"] * (det["fascia_2"]["fino_a"] - imponibile) / det["fascia_2"]["divisore"]

    elif imponibile <= det["fascia_3"]["fino_a"]:
        detrazioni = det["fascia_3"]["base"] * (det["fascia_3"]["fino_a"] - imponibile) / det["fascia_3"]["divisore"]

    else:
        detrazioni = 0

    add_regionale = imponibile * addizionale_regionale
    add_comunale = imponibile * addizionale_comunale

    #calcolo cuneo fiscale detrazioni

    if imponibile <= 20000:
        cuneo = 0  # TODO v2: somma non tassabile
    elif imponibile <= 32000:
        cuneo = 1000
    elif imponibile <= 40000:
        cuneo = 1000 * (40000 - imponibile) / 8000
    else:
        cuneo = 0

    irpef_netta = max(0, irpef_lorda - detrazioni - cuneo)

    ral_netta_annuale = round(imponibile - irpef_netta - add_comunale - add_regionale, 2)
    ral_netta_mensile = round(ral_netta_annuale / mensilita, 2)

    #costo azienda

    inps_datore = ral_lorda * config["costo_azienda"]["inps_datore"]
    tfr_divisore = ral_lorda/ config["costo_azienda"]["tfr_divisore"]
    inail = ral_lorda* config["costo_azienda"]["inail"]
    costo_azienda = ral_lorda + inps_datore + tfr_divisore + inail

    return RALResult(
    ral_lorda=round(ral_lorda, 2),
    mensilita=mensilita,
    inps=round(INPS, 2),
    imponibile=round(imponibile, 2),
    irpef_lorda=round(irpef_lorda, 2),
    detrazioni=round(detrazioni, 2),
    irpef_netta=round(irpef_netta, 2),
    addizionale_regionale=round(add_regionale, 2),
    addizionale_comunale=round(add_comunale, 2),
    netto_annuale=round(ral_netta_annuale, 2),
    netto_mensile=round(ral_netta_mensile, 2),
    costo_azienda=round(costo_azienda, 2)
    )
    