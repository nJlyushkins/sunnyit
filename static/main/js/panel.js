changed = false;

function makeAlert(alertInp, alert){
    alertInp.classList.remove('empty');
    alertInp.textContent = alert;
}

window.onload = function(){
    groupAdd = document.getElementById('group-add');
    groupConfirm = document.getElementById('group-confirm');
    groupName = document.getElementById('group-name');
    groupAlert = document.getElementById('group-alert');
    confirmAlert = document.getElementById('confirm-alert');
    group_id_inp = $('#group-add').find('input[name="group_id"]');
    confirm_id_inp = $('#group-confirm').find('input[name="group_id"]');
    group_name_inp = $('#group-name').find('input[name="name"]');
    btnGroupAdd = document.getElementById('add-group');

    btnGroupYes = document.getElementById('group-yes');
    btnGroupNo = document.getElementById('group-no');

    btnGroupYes.onclick = function(e){
        e.preventDefault();
        groupName.classList.add('hide');
        groupConfirm.classList.remove('hide');
        changed = true;
    }
    btnGroupNo.onclick = function(e){
        e.preventDefault();
        groupName.classList.add('hide');
        groupAdd.classList.remove('hide');
        group_id_inp.val('');
        changed = true;
    }

    btnGroupAdd.onclick = function(e){
        e.preventDefault();
        groupAdd.classList.remove('hide');
        changed = true;
    }

    groupAdd.onsubmit = function(e){
        e.preventDefault();
        formData = $('#group-add').serialize()
        group_id = group_id_inp.val();
        group_id = group_id.replace(/\s+/g, '');
        if(group_id == ''){
            makeAlert(groupAlert,'Вы ввели неправильное значение ID группы!');
            group_id_inp.val("");
            return 0;
        }else{
            if(!groupAlert.classList.contains('empty')){
                groupAlert.classList.add('empty');
            }
        }
        $.ajax({
            url: '/group-add',
            type: 'post',
            data:formData,
            success:function(res){
                try{
                    res_data = JSON.parse(res)
                }catch(e){
                    console.log(res);
                    return 0;
                }
                if(res_data['res'] == 'success'){
                    groupAdd.classList.add('hide');
                    groupName.classList.remove('hide');
                    group_name_inp.val(res_data['group']['name']);
                    confirm_id_inp.val(res_data['group']['id']);
                    document.getElementsByName('group_id')[1].setAttribute('readOnly','true');
                    console.log(res_data);
                }else{
                    makeAlert(groupAlert,res_data['error']);
                    group_id_inp.val("");
                    if(res_data['log']){
                        console.log(res_data['log']);
                    }
                    return 0;
                }
            }
        })
    }

    groupName.onsubmit = function (e){
        e.preventDefault();
    }

    groupConfirm.onsubmit = function(e){
        e.preventDefault();
        formData = $('#group-confirm').serialize();
        confirm_code = $('#group-confirm').find('input[name="code"]').val();
        confirm_code = confirm_code.replace(/\s+/g, '');
        if(confirm_code == ''){
            makeAlert(confirmAlert,'Введен неправильный код!');
            return 0;
        }else{
            if(!confirmAlert.classList.contains('empty')){
                confirmAlert.classList.add('empty');
            }
        }
        $.ajax({
            url: '/group-confirm',
            type: 'post',
            data:formData,
            success:function(res){
                try{
                    res_data = JSON.parse(res)
                }catch(e){
                    console.log(res);
                    return 0;
                }
                if(res_data['res'] == 'success'){
                    groupConfirm.classList.add('hide');
                    document.getElementsByName('group_id')[1].removeAttribute('readOnly','true');
                    console.log(res_data);
                    window.location.pathname = '/';
                }else{
                    makeAlert(confirmAlert,res_data['error']);
                    if(res_data['log']){
                        console.log(res_data['log']);
                    }
                    return 0;
                }
            }
        })
    }
}

window.addEventListener('click',function(e){
    if(!document.getElementById('group-name').contains(e.target)){
        if(!document.getElementById('group-name').classList.contains('hide')){
            if(!changed){
                document.getElementById('group-name').classList.add('hide');
            }else{
                changed = false;
            }
        }
    }
    if(!document.getElementById('group-add').contains(e.target)){
        if(!document.getElementById('group-add').classList.contains('hide')){
            if(!changed){
                document.getElementById('group-add').classList.add('hide');
            }else{
                changed = false;
            }
        }
    }
    if(!document.getElementById('group-confirm').contains(e.target)){
        if(!document.getElementById('group-confirm').classList.contains('hide')){
            if(!changed){
                document.getElementById('group-confirm').classList.add('hide');
            }else{
                changed = false;
            }
        }
    }
})