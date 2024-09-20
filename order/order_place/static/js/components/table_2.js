const Table2 = () => {
    const [data, setData] = React.useState([]);
    const [active, setActive] = React.useState('table_2');

    React.useEffect(() => {
        const handleActiveChange = () => {
            setActive(window.active);
        };
        window.addEventListener('activeChange', handleActiveChange);
        return () => {
            window.removeEventListener('activeChange', handleActiveChange);
        };
    }, []);

    const tableBodyRef = React.useRef(null);
    const tableHeadRef = React.useRef(null);

    React.useEffect(() => {
        const tableBody = tableBodyRef.current;
        const tableHead = tableHeadRef.current;

        if (tableBody && tableHead) {
            const scrollbarVisible = tableBody.scrollHeight > tableBody.clientHeight;
            if (scrollbarVisible && window.innerWidth > 1024) {
                tableHead.style.width = 'calc(100% - 17px)';
            } else {
                tableHead.style.width = '100%';
            }
        }
    }, [data]);

    React.useEffect(() => {
        if (active === 'table_1' || active === 'table_2') {
            setActive (0);
            const url = "/check_table";
            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const requestData = {
                'user': user,
                'table_name': "table_2"
            };
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
                setData(fetchedData['orders']);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
        }
    }, [active]);

    return (
        <>
            <table className="table_2" ref={tableHeadRef}>
                <thead className="table_2_head">
                    <tr>
                        <th>Order nr.</th>
                        <th>Order date</th>
                        <th>Order cost</th>
                        <th>Status</th>
                        <th>Info</th>
                    </tr>
                </thead>
            </table>

            <div className="table_2_body_container scrollable_orders" ref={tableBodyRef}>
                <table id="table_2_body" className="table_2_body">
                    <tbody id="table_2_body_tbody">
                        {data.length > 0 ? (
                            data.map((order, index) => (
                                <tr key={index}>
                                    <td>{order.order_id}</td>
                                    <td>{new Date(order.order_date).toLocaleDateString('ru-RU')}</td>
                                    <td>{order.order_price.toFixed(2)}€</td>
                                    <td>
                                        {order.status === -1 ? (
                                            <div className="status_status yellow_oval">Order</div>
                                        ) : order.status === 0 ? (
                                            <div className="status_status red_oval">Partial</div>
                                        ) : (
                                            <div className="status_status blue_oval">Full</div>
                                        )}
                                    </td>
                                    <td><input type="submit" className="info_input" value="Info" onClick={(event) => orderModal(event)} /></td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5">No data</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </>
    );
};

window.Table2 = Table2;
