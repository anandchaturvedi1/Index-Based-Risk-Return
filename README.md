# Index-Based-Risk-Return
A Python script to compute annualized risk and return based on a specified index computation methodology. It processes provided data to generate key financial metrics, risk assessment and performance evaluation

## Index Calculation  

```math
J_t = J_R \times \left[1 + \sum_{k=1}^{n} W_C \left(\frac{C_{k,t}}{C_{k,R}} - 1 \right) \right] \times \left(1 - \sum_{k=1}^{n} RC_C \frac{n}{220} \right)
```

## Weights & Costs  

| Underlying | $RC_C$ | $W_C$ |
|------------|--------|--------|
| 1 | 0.5%  | 10%  |
| 2 | 0.25% | 20%  |
| 3 | 0.1%  | 15%  |
| 4 | 0.1%  | 5%   |
| 5 | 0.25% | 30%  |
| 6 | 0.25% | 20%  |

## Definitions  

- **$J_0$** = 100 (Base: **12-Jan-2021**)  
- **$J_t$** = Index on day **t**  
- **R** = Last ref. Strategy Calc. Day (8th Business Day of Jan, Apr, Jul, Oct)  
- **$C_{k,t}$** = Component value on **t**  
- **$W_C$** = Component weight  
- **$RC_C$** = Rebalance cost  
- **n** = Days between **t** and **t-1**  

