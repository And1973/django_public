//ordered table adjust

function resizeItemsList() {
    let tbody = document.querySelector('.scrollable table tbody');
    let table = document.querySelector('#phones_list_table');
    if (tbody.clientHeight > 480 && window.innerWidth > 1200) {
        table.style.width = 'calc(100% - 17px)';
    } else {
        table.style.width = '100%';
    }
}
resizeItemsList();

function resizeOrderList(){
    let tbody = document.querySelector('.scrollable-ordered table tbody');
    let table = document.querySelector('#phones_ordered_table');
    if (tbody.clientHeight > 500 && window.innerWidth > 1024) {
        table.style.width = 'calc(100% - 17px)';
    } else {
        table.style.width = '100%';
    }
};
resizeOrderList();

//after initializing table values total adjust
function orderTotalAdjust(){
    let totalQty   = 0; 
    let totalPrice = 0;
    let items = document.getElementById('phones_ordered_table_tbody').querySelectorAll('tr');
    items.forEach(item => {
        totalQty     += parseInt(item.children[1].textContent, 10); 
        totalPrice   += parseFloat(item.children[2].textContent, 10);
    });
    let target = document.getElementById('phones_ordered_table_tbody_2');
    let totalQtyElement = document.querySelector('#order span');
    totalQtyElement.textContent = totalQty;
    if (totalQty > 0){
        target.querySelector('tr').children[1].textContent = totalQty;
        target.querySelector('tr').children[2].innerHTML = `${totalPrice.toFixed(2)}<span>€</span>`;
    } else {
        target.querySelector('tr').children[1].textContent = '';
        target.querySelector('tr').children[2].innerHTML = '';
    }
    if(totalQtyElement.classList.contains('start')){
        totalQtyElement.classList.remove('start');
    } else {
        if(totalQtyElement.classList.contains('colorChange')){
            totalQtyElement.classList.remove('colorChange');
            void totalQtyElement.offsetWidth;
            totalQtyElement.classList.add('colorChange');
            document.getElementById('icon').classList.remove('fillChange');
            void document.getElementById('icon').offsetWidth;
            document.getElementById('icon').classList.add('fillChange');
        } else {
            document.getElementById('icon').classList.add('fillChange');
            totalQtyElement.classList.add('colorChange');
        }
    }
};
orderTotalAdjust();

// order's table deletion
function orderTableDelete(){
    const table = document.getElementById('phones_ordered_table_tbody');
    if (table.childElementCount > 0){
        table.querySelectorAll('tr').forEach(item=>{
            item.remove();
        })
    }   
}
let switcher = 1;
// switch block
(()=>{
    const switch1 = document.querySelector('#table_1');
    const switch2 = document.querySelector('#table_2');
    const switch3 = document.querySelector('#table_3');
    const switch4 = document.querySelector('#table_4');
    const switch5 = document.querySelector('#table_5');
    const switch6 = document.getElementById('order');
    const table1 = document.querySelector('.grid-container');
    const table2 = document.querySelector('.table_2_container');
    const table3 = document.querySelector('.table_3_container');
    const table4 = document.querySelector('.table_4_container');
    const table5 = document.querySelector('.table_5_container');
    const table1_left = document.querySelector('.grid_item-1');
    const table1_right = document.querySelector('.grid_item-2');
    window.onload = switch2.style.background = '';
    window.onload = switch3.style.background = '';
    window.onload = switch4.style.background = '';
    window.onload = switch5.style.background = '';
    switch1.style.backgroundColor = '#9e9c9c';

    switch1.onclick = ()=>{
        if (switcher == 2 || switcher == 3 || switcher==4 || switcher == 5 || switcher == 6){
            table1.classList.remove('display_off');
            table1_right.classList.add('display_off');
            table1_left.classList.remove('display_off');
            switch1.style.backgroundColor = '#9e9c9c';
            table2.classList.add('display_off');
            switch2.style.backgroundColor = '';
            table3.classList.add('display_off');
            switch3.style.backgroundColor = '';
            table4.classList.add('display_off');
            switch4.style.backgroundColor = '';
            table5.classList.add('display_off');
            switch5.style.backgroundColor = '';
            updateTables();
            resizeOrderList();
            switcher = 1;
            window.active = "table_1";
            window.dispatchEvent(new Event('activeChange'));
        }
    }

    switch2.onclick = ()=>{
        if (switcher == 1 || switcher == 3 || switcher == 4 || switcher == 5 || switcher == 6){
            table1.classList.add('display_off');
            table1_left.classList.add('display_off');
            switch1.style.backgroundColor = '';
            table1_right.classList.add('display_off');
            table2.classList.remove('display_off');
            switch2.style.backgroundColor = '#9e9c9c';
            table2.classList.add('span');
            table3.classList.add('display_off');
            switch3.style.backgroundColor = ''; 
            table4.classList.add('display_off');
            switch4.style.backgroundColor = '';
            table5.classList.add('display_off');
            switch5.style.backgroundColor = '';
            removeHeaders();
            switcher = 2;
        }
    } 

    switch3.onclick = ()=>{
        if (switcher == 1 || switcher == 2 || switcher == 4 || switcher == 5 || switcher == 6){
            table1.classList.add('display_off');
            table1_left.classList.add('display_off');
            switch1.style.backgroundColor = '';
            table1_right.classList.add('display_off');
            table2.classList.add('display_off');
            switch2.style.backgroundColor = '';
            table3.classList.remove('display_off');
            switch3.style.backgroundColor = '#9e9c9c';
            table4.classList.add('display_off');
            switch4.style.backgroundColor = '';
            table5.classList.add('display_off');
            switch5.style.backgroundColor = '';
            removeHeaders();
            switcher=3;
        }
    }

    switch4.onclick = ()=>{
        if (switcher == 1 || switcher == 2 || switcher == 3 || switcher == 5 || switcher == 6){
            table1.classList.add('display_off');
            table1_left.classList.add('display_off');
            switch1.style.backgroundColor = '';
            table1_right.classList.add('display_off');
            table2.classList.add('display_off');
            switch2.style.backgroundColor = '';
            table3.classList.add('display_off');
            switch3.style.backgroundColor = '';
            table4.classList.remove('display_off');
            switch4.style.backgroundColor = '#9e9c9c';
            table5.classList.add('display_off');
            switch5.style.backgroundColor = '';
            removeHeaders();
            switcher=4;
            window.active = "table_4";
            window.dispatchEvent(new Event('activeChange'));
            
        }
    }

    switch5.onclick = ()=>{
        if (switcher == 1 || switcher == 2 || switcher == 3 || switcher == 4 || switcher == 6){
            table1.classList.add('display_off');
            table1_left.classList.add('display_off');
            switch1.style.backgroundColor = '';
            table1_right.classList.add('display_off');
            table2.classList.add('display_off');
            switch2.style.backgroundColor = '';
            table3.classList.add('display_off');
            switch3.style.backgroundColor = '';
            table4.classList.add('display_off');
            switch4.style.backgroundColor = '';
            table5.classList.remove('display_off');
            switch5.style.backgroundColor = '#9e9c9c';
            removeHeaders();
            switcher=5;
        }
    }

    switch6.onclick = ()=>{
        if (switcher == 1 || switcher == 2 || switcher == 3 || switcher == 4 || switcher == 5){
            table1_left.classList.add('display_off');
            switch1.style.backgroundColor = '';
            table2.classList.add('display_off');
            switch2.style.backgroundColor = '';
            table3.classList.add('display_off');
            switch3.style.backgroundColor = '';
            table4.classList.add('display_off');
            switch4.style.backgroundColor = '';
            table5.classList.add('display_off');
            switch5.style.backgroundColor = '';
            table1.classList.remove('display_off');
            table1_right.classList.remove('display_off');
            table1_right.classList.add('span');
            resizeOrderList();
            switcher=6;
            window.active = "table_6";
            window.dispatchEvent(new Event('activeChange'));
        }
    }

})();

var orderClose = document.getElementById('order');
var tableItems = document.querySelector('.grid_item-1');
var tableOrders = document.querySelector('.grid_item-2');
var welcome   = document.querySelector('.welcome');
var once = false;
var once2 = false;
var close = document.querySelectorAll('.table-header-close');
var table1 = document.querySelector('#phones_ordered_table');
var table2 = document.querySelector('#phones_ordered_table_table');
var header1 = document.querySelector('#phones_list_table');
var header2 = document.querySelector('#phones_list_table_table');

function removeHeaders(){
    let ttable2 = document.querySelector('.table_2');
    let ttable3 = document.querySelector('.table_3');
    let ttable5 = document.querySelector('.table_5');
    let modal   = document.querySelector('.table_order_modal_head');
    if(ttable2 && ttable3 && ttable5 && modal){
        if (window.innerWidth >= 768) {
            if( ttable2.classList.contains('display_off')){
                ttable2.classList.remove('display_off');
                ttable3.classList.remove('display_off');
                ttable5.classList.remove('display_off');
                modal.classList.remove('display_off');
            }
        } else {
            if( !ttable2.classList.contains('display_off')){
                ttable2.classList.add('display_off');
                ttable3.classList.add('display_off');
                ttable5.classList.add('display_off');
                modal.classList.add('display_off');
            }
        }
    } 
};

function openTable1_2(){
    if ( tableItems.classList.contains('display_off')){
        tableOrders.classList.add('display_off')
        tableOrders.classList.remove('span');
        tableItems.classList.remove('span')
        tableItems.classList.remove('display_off');
        tableOrders.classList.remove('display_off')
    } else { 
        tableItems.classList.remove('span');
        tableOrders.classList.remove('span');
        tableOrders.classList.remove('display_off');
    };
    orderClose.classList.add('display_off');
    once = false;
    once2 = false;
    if ( window.active ==='table_6'){
        document.querySelector('#table_1').style.backgroundColor = '#9e9c9c';
        switcher = 1;
        window.active = "table_1";
        window.dispatchEvent(new Event('activeChange'));    
    }
};

function closeTable1_2(){
    welcome.style.marginLeft = '0';
        orderClose.classList.remove('display_off');
        tableOrders.classList.add('display_off');
        tableItems.classList.add('span');
};


function updateTables() {
    resizeOrderList();
    removeHeaders();
    if (window.innerWidth > 1200) {
        if ( !tableItems.classList.contains('display_off') && !tableOrders.classList.contains('display_off')){
            return;
        } else {
            openTable1_2();
        }
    } else {
        if (window.innerWidth <= 768){
            if(once2 == true){
                return;
            }
            for (var cl of close){
                cl.classList.add ('display_off'); 
            }
            once2 = true;
            if ( !tableItems.classList.contains('display_off')){
                closeTable1_2();
            }
            return;
        }
        let totalQtyElement = document.querySelector('#order span');
        if(totalQtyElement.classList.contains('colorChange')){
            totalQtyElement.classList.remove('colorChange');
            void totalQtyElement.offsetWidth;
            document.getElementById('icon').classList.remove('fillChange');
            void document.getElementById('icon').offsetWidth;
        }
        if(once2 == true){
            for (var cl of close){
                cl.classList.remove('display_off'); 
            }
            once2 = false;
        }
        if(once == true){
            return;
        }
        if ( !tableItems.classList.contains('display_off')){
            closeTable1_2();
        }
        once = true;
    }
    
};

updateTables();
window.addEventListener('resize', updateTables);

function startInactivityTimer() {
    let time;
    document.onmousemove = resetTimer;
    function logout() {
        alert("Session finished")
        window.location.href = "/";
    };
    function resetTimer() {
        clearTimeout(time);
        time = setTimeout(logout, 2000000);
    };
    resetTimer();
};
startInactivityTimer();

