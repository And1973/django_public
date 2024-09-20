const Table5 = () => {
    const [data, setData] = React.useState([]);
    const [total, setTotal] = React.useState(0);
    const [active, setActive] = React.useState('table_5');
    React.useEffect(() => {
        const handleActiveChange = () => {
            setActive(window.active);
            //onsole.log("inside table_5 set active", active)
        };
        window.addEventListener('activeChange', handleActiveChange); 
        return () => {
            window.removeEventListener('activeChange', handleActiveChange);
        };
    }, []);
    
    React.useEffect(() => {
        if (active === "table_3" || active === "table_5") {
            setActive (0);
            const url = "/check_table";
            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const requestData = {
                'user': user,
                'table_name': active === "table_5"?"table_5":"table_5_no_rebalance"
            };
            const delay = active === "table_5" ? 0 : 1000;
            setTimeout(() =>{
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(requestData)
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Server error in checkAddition request');
                    }
                    return response.json();
                })
                .then(fetchedData => {
                    setData(fetchedData['balance'].balance);
                    setTotal(fetchedData['balance'].total);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                });
            }, delay);
        };
    }, [active]);

    return (
        <>
            <table className="table_5">
                <thead className="table_5_head">
                    <tr>
                        <th>Name</th>
                        <th>Date</th>
                        <th>Invoice sum</th>
                        <th>Transfer sum</th>
                    </tr>
                </thead>
            </table>    
            <div className="table_5_body_container">
                <table className="table_5_body">
                    <tbody id="table_5_body_tbody">
                        {data.length > 0 ? (
                            data.map((balance, index) => (
                                <tr key={index}>
                                    <td>{balance.name}</td>
                                    <td>{new Date(balance.date).toLocaleDateString('ru-RU')}</td>
                                    {balance.name.includes("PVZ") ? (
                                        <>
                                            <td>{balance.sum.toFixed(2)}€</td>
                                            <td></td>
                                        </>
                                    ) : (
                                        <>
                                            <td></td>
                                            <td>{balance.sum.toFixed(2)}€</td>
                                        </>
                                    )}
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="4">No data</td>
                            </tr>
                        )}
                    </tbody>
                </table>
                {data.length > 0 && (
                    <div className="table_5_total_cont">
                        <p className="table_5_total_left">Total:</p>
                        <p className="table_5_empty_1"></p>
                        <p className="table_5_empty_2"></p>
                        <p className="table_5_total_right">{total.toFixed(2)}€</p>
                    </div>
                )}
                <div className="table_5_total_btn">
                    <p className="table_5_total_left"></p>
                    <p className="table_5_empty_1"></p>
                    <p className="table_5_empty_2"></p>
                    <div className="button">
                        <button className="balance_btn display_off" type="submit">Download</button>
                    </div>
                </div>
            </div>
        </>
    );
};

window.Table5 = Table5;
