
from .schemas import RALResult

import plotly.graph_objects as go

def create_waterfall(risultato: RALResult):

    
    fig = go.Figure(go.Waterfall(
        x=["RAL Lorda", "INPS", "IRPEF Lorda", "Detrazioni", "Add. Reg.", "Add. Com.", "Netto Annuale"],
        y=[risultato.ral_lorda, -risultato.inps, -risultato.irpef_lorda, risultato.detrazioni, -risultato.addizionale_regionale, -risultato.addizionale_comunale, risultato.netto_annuale],
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        text=[f"€{risultato.ral_lorda:,.0f}", f"-€{risultato.inps:,.0f}", f"-€{risultato.irpef_lorda:,.0f}", f"+€{risultato.detrazioni:,.0f}", f"-€{risultato.addizionale_regionale:,.0f}", f"-€{risultato.addizionale_comunale:,.0f}", f"€{risultato.netto_annuale:,.0f}"],
        textposition="outside",
        decreasing={"marker": {"color": "#e74c3c"}},
        increasing={"marker": {"color": "#2ecc71"}},
        totals={"marker": {"color": "#3498db"}},
        textfont={"size": 13}
    ))


    fig.update_layout(
        title=f"Costo Azienda: €{risultato.costo_azienda:,.0f} | Lordo Mensile: €{risultato.ral_lorda/risultato.mensilita:,.0f} | Mensile netto: €{risultato.netto_mensile:,.0f}",
        template="plotly_dark",
        modebar={"remove": ["zoom", "pan", "select", "lasso", "zoomIn", "zoomOut", "autoScale", "resetScale"]},
        showlegend=False,
        height=500,
        width=600,
    )

    return fig