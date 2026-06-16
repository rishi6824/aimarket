"""
Stocks & Trading Bot Router
"""
from fastapi import APIRouter, HTTPException
from models import StockPredictionRequest, StockPredictionResponse, TradeRequest, TradeResponse, PortfolioResponse, Holding
from services.stocks_client import get_intraday_data
from services import supabase_client
from services.groq_client import chat_completion

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])

@router.post("/predict", response_model=StockPredictionResponse)
async def predict_stock(req: StockPredictionRequest):
    try:
        # Fetch data
        data = await get_intraday_data(req.symbol)
        
        time_series = data.get("Time Series (1min)", {})
        if not time_series:
            raise ValueError("No time series data found for this symbol. It may be invalid or delisted.")
            
        # Get the latest 10 data points for AI analysis
        latest_times = list(time_series.keys())[:10]
        recent_data = {t: time_series[t] for t in latest_times}
        
        current_price = float(time_series[latest_times[0]]["4. close"])
        
        # Analyze with AI
        prompt = f"""You are an elite quantitative analyst and day trader.
Analyze the following recent 1-minute intraday data for {req.symbol} and provide a rapid trading prediction (Buy / Sell / Hold) with a sharp, 2-sentence rationale. 
Current Price: ${current_price}

Recent Data:
{recent_data}

Provide ONLY the prediction and rationale. Be decisive."""

        prediction = await chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300,
        )
        
        # Format the time_series for the frontend chart (limit to last 60 points)
        chart_data = {}
        chart_times = list(time_series.keys())[:60]
        chart_times.reverse() # chronological order for chart
        for t in chart_times:
            chart_data[t] = float(time_series[t]["4. close"])
            
        return StockPredictionResponse(
            symbol=req.symbol.upper(),
            prediction=prediction,
            current_price=current_price,
            time_series_data=chart_data
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Stock Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock prediction. Check API limits or symbol.")

@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio():
    try:
        portfolios = await supabase_client.select("portfolios", {"user_id": "default_user"})
        if not portfolios:
            raise HTTPException(status_code=404, detail="Portfolio not found.")
        portfolio = portfolios[0]
        
        holdings_data = await supabase_client.select("portfolio_holdings", {"portfolio_id": portfolio["id"]})
        
        holdings = []
        for h in holdings_data:
            if float(h["quantity"]) > 0:
                holdings.append(Holding(
                    symbol=h["symbol"],
                    quantity=float(h["quantity"]),
                    avg_price=float(h["avg_price"])
                ))
                
        total_value = float(portfolio["balance"]) + sum(h.quantity * h.avg_price for h in holdings)
        
        return PortfolioResponse(
            balance=float(portfolio["balance"]),
            holdings=holdings,
            total_value=total_value
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trade", response_model=TradeResponse)
async def execute_trade(req: TradeRequest):
    try:
        portfolios = await supabase_client.select("portfolios", {"user_id": "default_user"})
        if not portfolios:
            raise HTTPException(status_code=404, detail="Portfolio not found.")
        portfolio = portfolios[0]
        
        total_value = req.quantity * req.price
        
        holdings_data = await supabase_client.select("portfolio_holdings", {"portfolio_id": portfolio["id"], "symbol": req.symbol})
        holding = holdings_data[0] if holdings_data else None
        
        if req.action == "BUY":
            if float(portfolio["balance"]) < total_value:
                raise ValueError("Insufficient virtual funds.")
            
            new_balance = float(portfolio["balance"]) - total_value
            await supabase_client.update("portfolios", portfolio["id"], {"balance": new_balance})
            
            if holding:
                new_qty = float(holding["quantity"]) + req.quantity
                total_cost = (float(holding["quantity"]) * float(holding["avg_price"])) + total_value
                new_avg = total_cost / new_qty
                await supabase_client.update("portfolio_holdings", holding["id"], {"quantity": new_qty, "avg_price": new_avg})
            else:
                await supabase_client.insert("portfolio_holdings", {
                    "portfolio_id": portfolio["id"],
                    "symbol": req.symbol,
                    "quantity": req.quantity,
                    "avg_price": req.price
                })
                
        elif req.action == "SELL":
            if not holding or float(holding["quantity"]) < req.quantity:
                raise ValueError("Insufficient shares to sell.")
                
            new_balance = float(portfolio["balance"]) + total_value
            await supabase_client.update("portfolios", portfolio["id"], {"balance": new_balance})
            
            new_qty = float(holding["quantity"]) - req.quantity
            await supabase_client.update("portfolio_holdings", holding["id"], {"quantity": new_qty})
            
        trade = await supabase_client.insert("trades", {
            "portfolio_id": portfolio["id"],
            "symbol": req.symbol,
            "action": req.action,
            "quantity": req.quantity,
            "price": req.price,
            "total_value": total_value
        })
        
        return TradeResponse(
            status="success",
            message=f"Successfully executed {req.action} order for {req.quantity} shares of {req.symbol}.",
            trade=trade
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trades():
    try:
        portfolios = await supabase_client.select("portfolios", {"user_id": "default_user"})
        if not portfolios:
            return {"trades": []}
        portfolio_id = portfolios[0]["id"]
        
        trades = await supabase_client.select("trades", {"portfolio_id": portfolio_id}, limit=50)
        return {"trades": trades}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
