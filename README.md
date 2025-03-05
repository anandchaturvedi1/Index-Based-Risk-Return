# Index-Based-Risk-Return
A Python script to compute annualized risk and return based on a specified index computation methodology. It processes provided data to generate key financial metrics, risk assessment and performance evaluation

## Index Level Calculation  

Index levels **$$J_t$$** for all Strategy Calculation Days **t** are computed using the following formula:  

$$
J_t = J_R \times \left[1 + \sum_{k=1}^{n} W_C \times \left(\frac{C_{k,t}}{C_{k,R}} -1 \right) \right] \times \left(1 - \sum_{k=1}^{n} RC_C \times \frac{n}{220} \right)
$$

### Component Weights and Rebalance Costs  

| Underlying | Rebalance Cost ($$RC_C$$) | Weight ($$W_C$$) |
|------------|------------------|------------|
| Underlying 1 | 0.5% | 10% |
| Underlying 2 | 0.25% | 20% |
| Underlying 3 | 0.1% | 15% |
| Underlying 4 | 0.1% | 5% |
| Underlying 5 | 0.25% | 30% |
| Underlying 6 | 0.25% | 20% |

### Definitions  

- **$$J_0$$**: Initial index level set to **100** on the base date **$$t_0$$**.  
- **$$J_t$$**: Index levels on the Index Calculation Day **t**.  
- **t**: An Index Calculation Day, when **London is open for trading**.  
- **$$t_0$$**: **12-Jan-2021**, the base date.  
- **R**: The last reference Strategy Calculation Day, occurring on the **8th Business Day of every 8th Index Calculation Day** in **January, April, July, and October** each year.  
- **n**: The number of underlying components.  
- **$$C_(k,t)$$**: The value of the **k-th underlying component** of Index **J** on Strategy Calculation Day **t**.  
- **$$W_C$$**: The weight assigned to each underlying component **C**.  
- **$$RC_C$$**: The rebalance cost associated with each underlying component **C**.  
- **n**: The difference in days between **t** and **t-1**.  

This formula ensures accurate computation of index levels while accounting for component weight adjustments and rebalancing costs.  

