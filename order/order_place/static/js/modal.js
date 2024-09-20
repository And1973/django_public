async function orderModal(element){
    var modal = document.getElementById("order_modal");
    var span = document.getElementById("order_close");
    modal.style.display = "flex";
    span.onclick = () => {
        modal.style.display = "none";
        document.getElementById("table_order_modal_body_tbody").innerHTML = '';
    }
    let window = 'order';
    let id = element.target.parentElement.parentElement.firstElementChild.textContent;
    checkModal(window, id).then( result => {
        if( result.qty){
            createOrderModalElement(result.items_list)
            let tableContainer = document.getElementById("table_order_modal_body_tbody");
            let tableHeader = document.querySelector(".table_order_modal");
            if (tableContainer.scrollHeight <= 350 ) {
                tableHeader.style.width = '100%';
            } else {
                tableHeader.style.width = 'calc(100% - 17px)';
            }
        };
    });
}

async function checkModal(table, id) {
    try {
        const url = "/modal";
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const data = {
            'id':  id,
            'table_name': table,
        };
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error('Server error in modalAddition request');
        }
        return await response.json();
    } 
    catch (error) {
        console.error('Front error in modalAddition request', error);
    }
}


function createOrderModalElement( items_list){
    items_list.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${ item[0] }</td>
            <td>${ item[1] }</td>
            <td>${ item[2].toFixed(2)}</td>
            <td>${ (item[1] * item[2]).toFixed(2) }<span>€</span></td>
        `;
        let table_body = document.getElementById('table_order_modal_body_tbody');
        table_body.appendChild(tr);

        let items  = document.getElementById('table_order_modal_body_tbody').querySelectorAll('tr');
        let total = document.getElementById('table_order_modal_body_tbody_2');
        let totalQty   = 0; 
        let totalPrice = 0;
        items.forEach(item => {
            totalQty     += parseInt(item.children[1].textContent, 10); 
            totalPrice   += parseFloat(item.children[3].textContent, 10);
        });
        total.querySelector('tr').children[1].textContent = totalQty;
        total.querySelector('tr').children[3].innerHTML = `${totalPrice.toFixed(2)}<span>€</span>`;
        
    });
}