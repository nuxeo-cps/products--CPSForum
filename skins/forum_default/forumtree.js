function changeVisibility(id) {
    el = document.getElementById('thread_'+id);
    im = document.getElementById(id+'_img');

    // using xDef is ie-compliant
    visibility = (xDef(el.visibility) && el.visibility) || (xDef(el.style.visibility) && el.style.visibility)
    if(visibility!="hidden") {
        im.src = '/p_/pl';
        xHide(el);
        el.hidden_innerHTML = el.innerHTML;
        el.innerHTML = "";
    } else {
        im.src = '/p_/mi';
        xShow(el);
        if(xDef(el.hidden_innerHTML)) { el.innerHTML = el.hidden_innerHTML; }
    }
}

function changeAll(state) {
    alert(state);
    tlist = top_threads;
    for(i=0;i<tlist.length;i++) {
      item = document.getElementById(tlist[i]);
      if(item.id.substring(0,"thread_".length) == 'thread_') {
          if(state) {
            xShow(item);
            if(xDef(item.hidden_innerHTML)) { item.innerHTML = item.hidden_innerHTML; }
          } else {
            xHide(item);
            item.hidden_innerHTML = item.innerHTML;
            item.innerHTML = "";
          }
      }
    }
}
function selectAll(state) {
    tlist = document.getElementsByTagName("input");
    for(i=0;i<tlist.length;i++) {
      item = tlist[i];
      if(item.name.substring(0,"forum_thread_ids:list".length) == 'forum_thread_ids:list') {
        item.checked = state;
      }
    }
}

