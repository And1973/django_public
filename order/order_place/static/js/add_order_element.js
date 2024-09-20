function add_order_element( element ) {
    var buttonTd = element.parentElement;
    var textInputTd = buttonTd.previousElementSibling;
    var textInput = textInputTd.querySelector('input');
    qty_ordered = textInput.value;
    if (!qty_ordered){
        textInput.style.borderColor = "red";
        setTimeout( function (){
            textInput.style.borderColor = "";
        }, 1000);
    }
    else{
	createElement( element.dataset.id, qty_ordered, element.dataset.name, element.dataset.price, element, textInput ).then(order_id =>{
        create_order_element(element, order_id, qty_ordered);
        resizeOrderList();
        orderTotalAdjust();
        textInput.value= "";
        }).catch( error => {
            alert(error);
        });
    }
}

async function createElement(id, quantity, name, price, element, input) {
    try {
        const vat = document.getElementById('vat');
        if (vat.textContent === "Invalid"){
            input.value = '';
            throw new Error('VAT not valid');
        };
        var table_body = document.getElementById('phones_ordered_table_tbody');
        if (table_body.childElementCount > 0){
            var same_id_elements = table_body.querySelectorAll("#"+element.dataset.id);
            var order_id; 
            var input;
            if (same_id_elements){
                same_id_elements.forEach( e => {
                    if ( e.dataset.order_status === "True"){
                        order_id = e.lastElementChild.firstElementChild.dataset.order_id;   
                    }
                })
            }
            if (order_id){
                const response = await fetch("/api/order/check/?order_id=" + order_id);
                if (response.status == 200){
                    const responsejson = await response.json();
                    editable = responsejson['editable'];
                    if (editable){
                        input.value ="";
                        throw new Error("Already ordered") ;
                    }
                    else{
                        orderTableDelete();
                    } 
                }
            }
            table_body = document.getElementById('phones_ordered_table_tbody');
            if (table_body.childElementCount > 0){
                var other_elements_last_child_order_id = table_body.lastElementChild.lastElementChild.firstChild.dataset.order_id;
                if (other_elements_last_child_order_id){
                    const response = await fetch("/api/order/check/?order_id=" + other_elements_last_child_order_id);
                    if (response.status == 200){
                        const responsejson = await response.json();
                        editable = responsejson['editable'];
                        if (editable){
                            input.value ="";
                        }
                        else{
                            orderTableDelete();
                        } 
                    }
                }
            }
        }
        const url = "/api/order/get/?id=" + id.slice(3) + "&quantity=" + quantity;
        const response1 = await fetch(url);
        if (response1.ok) {
            const rjson = await response1.json();
            if (rjson['available']){
                const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                const url = "/api/order/create"
                const data = {
                    'id': id.slice(3),
                    'name': name,
                    'price':price,
                    'qty': quantity

                };
                const response2 = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(data)
                });
                const response2json = await response2.json();
                return  (response2json['order_id']);
            } else {
                throw new Error('Stock not available');
            };
        };   
    } catch (error) {
        throw error.message;
    }
}

function create_order_element( element, order_id, qty_ordered){
    const tr = document.createElement('tr');
    tr.id = element.dataset.id
    tr.setAttribute('data-order_status', 'True');
    tr.innerHTML = `
        <td align="left" class="given" ondblclick="itemGiven(event,this)">${element.dataset.name}</td>
        <td align="right">${qty_ordered}</td>
        <td align="right">${(element.dataset.price*qty_ordered).toFixed(2)}€</td>
        <td><input type="text" size="1" data-total_qty = '${element.dataset.qty}' data-order_qty = '${qty_ordered}'  oninput="allowOnlyNumbers(event)" /></td>
        <td><input type="submit" data-phone_id='${element.dataset.id}' data-order_id='${order_id}' data-price='${element.dataset.price}' onclick="edit_order_element(this)" value="Update" /></td>
        <td><input type="submit" data-phone_id='${element.dataset.id}' data-order_id='${order_id}' onclick="delete_order_element(this)" value="Delete" /></td>
    `;
    let table_body = document.getElementById('phones_ordered_table_tbody');
    table_body.appendChild(tr);
}

    