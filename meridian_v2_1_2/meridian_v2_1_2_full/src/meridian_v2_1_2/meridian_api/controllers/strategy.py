"""Strategy Controller"""
from fastapi import APIRouter, HTTPException
from ..schemas import PriceSeries
from ..core.engine_loader import loader
import pandas as pd

router = APIRouter(prefix="/strategy", tags=["Strategy"])

@router.post("/evolve")
async def evolve_strategy(request: PriceSeries, generations: int = 10):
    """Evolve trading strategy using genetic programming"""
    try:
        price = pd.Series(request.prices, index=pd.to_datetime(request.timestamps))
        best_genome, history = loader.genetic_engine.evolve(price, generations=generations)
        
        return {
            "best_genome": best_genome.genes,
            "fitness_history": history,
            "final_fitness": history[-1] if history else 0,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

