const Table3 = () => {
    const [data, setData] = React.useState([]);
    const [active, setActive] = React.useState('table_3');

    React.useEffect(() => {
        const handleActiveChange = () => {
            setActive(window.active);
            //console.log("inside table_3 set active", active)
        };
        window.addEventListener('activeChange', handleActiveChange);

        return () => {
            window.removeEventListener('activeChange', handleActiveChange);
        };
    }, []);
    
    
        React.useEffect(() => {
            if (active === 'table_3' || active === 'table_5') {
                setActive (0);
                const url = "/check_table";
                const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                const requestData = {
                    'user': user,
                    'table_name': active === "table_3"?"table_3":"table_3_no_rebalance"
                };
                const delay = active === "table_3" ?  0: 1000;
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
                        setData(fetchedData['invoice']);
                    })
                    .catch(error => {
                        console.error('Error fetching data:', error);
                    });
                }, delay);
            };
        }, [active]);
    

    return (
        <>
            <table className="table_3">
                <thead className="table_3_head">
                    <tr>
                        <th>Invoice Nr.</th>
                        <th>Invoice date</th>
                        <th>Invoice cost</th>
                        <th>Status</th>
                        {/* <th>Check</th> */}
                        <th>Download</th>
                    </tr>
                </thead>
            </table>
            <div className="table_3_body_container">
                <table className="table_3_body">
                    <tbody id="table_3_body_tbody">
                        {data.length > 0 ? (
                            data.map((invoice, index) => (
                                <tr key={index}>
                                    <td>{invoice.invoice_id}</td>
                                    <td>{new Date(invoice.invoice_date).toLocaleDateString('ru-RU')}</td>
                                    <td>{invoice.invoice_price.toFixed(2)}€</td>
                                    <td>
                                        {invoice.invoice_status ? (
                                            <div className="status_status blue_oval">Paid</div>
                                        ) : (
                                            <div className="status_status red_oval">Unpaid</div>
                                        )}
                                    </td>
                                    {/* <td><input className="info_input" type="submit" value="Check" /></td> */}
                                    {invoice.invoice_url ? (
                                        <td>
                                            {/* <a href={invoice.invoice_url} download>
                                                <input className="info_input" type="submit" value="Download" />
                                            </a> */}
                                            <button className="info_input" onClick={() => window.location.href = invoice.invoice_url}>Download</button>
                                        </td>
                                    ) : (
                                        <td><button className="info_input" type="submit" disabled>Download</button></td>
                                    )}
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="6">No data</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </>
    );
};

window.Table3 = Table3;
