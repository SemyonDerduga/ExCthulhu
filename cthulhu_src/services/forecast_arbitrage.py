"""
Интегрированный сервис для поиска арбитража с прогнозированием.
"""

from typing import List, Optional, Dict, Any
import logging
from dataclasses import dataclass

from cthulhu_src.services.processor import find_paths, AdjacencyList, NodeID
from cthulhu_src.services.forecast import ForecastService, Forecast

logger = logging.getLogger("excthulhu")


@dataclass
class ArbitrageOpportunity:
    """Арбитражная возможность с прогнозом."""
    
    path: List[tuple]
    profit_percent: float
    forecast: Optional[Forecast] = None
    forecast_confidence: float = 0.0
    recommended_action: str = "hold"  # buy, sell, hold


class ForecastArbitrageService:
    """
    Сервис для поиска арбитража с интегрированным прогнозированием.
    
    Этот сервис:
    1. Находит арбитражные возможности
    2. Анализирует исторические данные для прогнозирования
    3. Рекомендует действия на основе прогнозов
    """
    
    def __init__(self, lookback: int = 60, forecast_method: str = "mean"):
        self.forecast_service = ForecastService(lookback=lookback)
        self.forecast_method = forecast_method
    
    def find_opportunities_with_forecast(
        self,
        adj_list: AdjacencyList,
        start_node: NodeID,
        start_amount: float,
        max_depth: int = 5,
        prune_ratio: float = 0.0,
        num_workers: Optional[int] = None,
        historical_prices: Optional[List[float]] = None,
        forecast_horizon: int = 5,
    ) -> List[ArbitrageOpportunity]:
        """
        Найти арбитражные возможности с прогнозированием.
        
        Args:
            adj_list: Граф обменных курсов
            start_node: Начальная валюта
            start_amount: Начальное количество
            max_depth: Максимальная глубина поиска
            prune_ratio: Коэффициент отсечения
            num_workers: Количество рабочих процессов
            historical_prices: Исторические цены для прогнозирования
            forecast_horizon: Горизонт прогнозирования (в минутах)
        
        Returns:
            Список арбитражных возможностей с прогнозами
        """
        # Найти базовые арбитражные возможности
        paths = find_paths(
            adj_list, start_node, start_amount, 
            max_depth=max_depth, prune_ratio=prune_ratio, 
            num_workers=num_workers
        )
        
        opportunities = []
        
        for path in paths:
            # Рассчитать прибыль
            profit_percent = self._calculate_profit_percent(path, start_amount)
            
            # Создать базовую возможность
            opportunity = ArbitrageOpportunity(
                path=path,
                profit_percent=profit_percent
            )
            
            # Добавить прогноз если есть исторические данные
            if historical_prices and len(historical_prices) >= self.forecast_service.lookback + forecast_horizon:
                try:
                    forecast = self.forecast_service.predict(
                        historical_prices, [forecast_horizon], self.forecast_method
                    )[0]
                    
                    opportunity.forecast = forecast
                    opportunity.forecast_confidence = self._calculate_confidence(forecast)
                    opportunity.recommended_action = self._get_recommendation(forecast, profit_percent)
                    
                except Exception as e:
                    logger.warning(f"Ошибка прогнозирования: {e}")
            
            opportunities.append(opportunity)
        
        # Сортировать по прибыльности и уверенности прогноза
        opportunities.sort(
            key=lambda x: (x.profit_percent * (1 + x.forecast_confidence)), 
            reverse=True
        )
        
        return opportunities
    
    def _calculate_profit_percent(self, path: List[tuple], start_amount: float) -> float:
        """Рассчитать процент прибыли для пути."""
        if len(path) < 2:
            return 0.0
        
        final_amount = path[-1][1]
        return ((final_amount - start_amount) / start_amount) * 100
    
    def _calculate_confidence(self, forecast: Forecast) -> float:
        """Рассчитать уверенность прогноза на основе стандартного отклонения."""
        if forecast.sigma == 0:
            return 1.0
        # Чем меньше стандартное отклонение, тем выше уверенность
        return max(0.0, 1.0 - (forecast.sigma / abs(forecast.mu)))
    
    def _get_recommendation(self, forecast: Forecast, profit_percent: float) -> str:
        """
        Получить рекомендацию на основе прогноза и прибыльности.
        
        Returns:
            "buy" - рекомендуется покупать
            "sell" - рекомендуется продавать  
            "hold" - рекомендуется держать
        """
        if forecast.mu > 0.01:  # Ожидается рост > 1%
            if profit_percent > 0.5:  # Прибыль > 0.5%
                return "buy"
            else:
                return "hold"
        elif forecast.mu < -0.01:  # Ожидается падение > 1%
            return "sell"
        else:
            return "hold"
    
    def analyze_market_trends(
        self, 
        historical_prices: List[float], 
        horizons: List[int] = [1, 5, 15]
    ) -> Dict[str, Any]:
        """
        Анализировать рыночные тренды.
        
        Returns:
            Словарь с анализом трендов
        """
        try:
            forecasts = self.forecast_service.predict(
                historical_prices, horizons, self.forecast_method
            )
            
            trend_analysis = {
                "short_term": forecasts[0] if len(forecasts) > 0 else None,
                "medium_term": forecasts[1] if len(forecasts) > 1 else None,
                "long_term": forecasts[2] if len(forecasts) > 2 else None,
                "overall_trend": "bullish" if forecasts[0].mu > 0 else "bearish" if forecasts[0].mu < 0 else "neutral"
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа трендов: {e}")
            return {"error": str(e)} 