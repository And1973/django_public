var slice = new Map()
var map = new Map()

function init(){
    var rows = document.querySelectorAll('#phones_list_table_tbody tr td:nth-child(5) input');
    for (var row of rows ){
        var dataId = row.dataset.id;
        var dataName = row.dataset.name;
        var dataQty = row.dataset.qty;
        var dataPrice = row.dataset.price;
        map.set(dataId, [dataName, dataQty, dataPrice])
    };
};
init();

function reset_phones_list(){
    var text = document.getElementById("search_input");
    if (text.value){
        text.value = "";
        var tbody = document.getElementById('phones_list_table_tbody');
        tbody.innerHTML = '';
        create_list_element(map, tbody);
        resizeItemsList();
    }
}

document.getElementById('search_input').addEventListener('input', function() {
    search(this.value);
});

function allowOnlyNumbers(event) {
    event.target.value = event.target.value.replace(/[^0-9]/g, '');   
    var parenttbody = event.target.parentElement.parentElement.parentElement;

    if (parenttbody){
        if( parenttbody.id !== 'phones_ordered_table_tbody'){
            if (parseInt(event.target.value,10) <= parseInt(event.target.dataset.qty,10)){
                console.log(event.target.value + " " + event.target.dataset.qty);
                return;
            }    
            else{
                console.log(event.target.value + " " + event.target.dataset.qty);
                event.target.value = event.target.value.slice(0,-1);
            }
        }
        else{
            const id = event.target.parentNode.nextElementSibling.firstElementChild.dataset.phone_id;
            const table = document.getElementById('phones_list_table_tbody')
            const elem = table.querySelector(`#${id}`);
            const total_elem_qty = elem.lastElementChild.firstElementChild.dataset.qty
            if ( total_elem_qty ){
                if ( parseInt(event.target.value,10) <= parseInt(total_elem_qty,10 )){
                    console.log( event.target.value + " " + event.target.dataset.order_qty+ " " + total_elem_qty );
                    return;
                }
                else{
                    console.log(event.target.value + " " + event.target.dataset.qty);
                    event.target.value = event.target.value.slice(0,-1);
                }
            }    
        }
    }
}

function search( text ) {
    if ( text ) {
        slice = new Map();
        map.forEach(function(value, key) {
            string = text.replace(/\s+/g, '').toLowerCase();
            substring = value[0].replace(/\s+/g, '').toLowerCase();
            if ( substring.includes( string ) ) {
                slice.set(key, value);
                }
        });
        var tbody = document.getElementById('phones_list_table_tbody');
        tbody.innerHTML = '';
        create_list_element(slice, tbody);
        resizeItemsList();
    }
}

function create_list_element(new_array, table_body) {
    new_array.forEach( function (value,key){
        const tr = document.createElement('tr');
        tr.id = key;
        tr.innerHTML = `
            <td align="left">${value[0]}</td>
            <td align="right">${value[1]}</td>
            <td align="right">${value[2]}€</td>
            <td><input type="text" size="1" data-qty="${value[1]}" oninput="allowOnlyNumbers(event)"/></td>
            <td><input type="submit" data-id='${key}' data-name='${value[0]}' data-qty='${value[1]}' data-price='${value[2]}' onclick = "add_order_element(this)" value="Order" /></td>
        `;
        table_body.appendChild(tr);
    });
}