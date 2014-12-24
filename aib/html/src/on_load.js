function on_load() {

  document.body.innerHTML = '';  // clear welcome screen

  task_div = document.createElement('div');
  task_div.style.background = 'lightblue';
  task_div.style.height = max_h-15 + 'px';
  task_div.style.width = '33%';
  task_div.style.border = '1px solid black';
  task_div.style[cssFloat] = 'left';
  var task_hdng = document.createElement('div');
  task_hdng.className = 'main_heading';
  var task_text = document.createTextNode('Task List');
  task_hdng.appendChild(task_text);
  task_div.appendChild(task_hdng);
  task_div.id = 'debug2';
  document.body.appendChild(task_div);

  menu_div = document.createElement('div');
  menu_div.style.background = 'lightgreen';
  menu_div.style.height = max_h-15 + 'px';
  menu_div.style.width = '33%';
  menu_div.style.borderTop = '1px solid black';
  menu_div.style.borderBottom = '1px solid black';
  menu_div.style.borderRight = '1px solid black';
  menu_div.style[cssFloat] = 'left';
  var menu_hdng = document.createElement('div');
  menu_hdng.className = 'main_heading';
  var menu_text = document.createTextNode('Menu');
  menu_hdng.appendChild(menu_text);
  menu_div.appendChild(menu_hdng);
  document.body.appendChild(menu_div);
  // store menu_div.height for tree.js, so it knows when to overflow
  menu_div.height = menu_div.offsetHeight - menu_hdng.offsetHeight;

  favr_div = document.createElement('div');
  favr_div.style.background = 'pink';
  favr_div.style.height = max_h-15 + 'px';
  favr_div.style.width = '33%';
  favr_div.style.borderTop = '1px solid black';
  favr_div.style.borderBottom = '1px solid black';
  favr_div.style.borderRight = '1px solid black';
  favr_div.style[cssFloat] = 'left';
  var favr_hdng = document.createElement('div');
  favr_hdng.className = 'main_heading';
  var favr_text = document.createTextNode('Favourites');
  favr_hdng.appendChild(favr_text);
  favr_div.appendChild(favr_hdng);
  favr_div.id = 'debug3';
  document.body.appendChild(favr_div);

//  window_id = Math.random();
  var ca = document.cookie.split(';');
  var name = 'session_id=';
  for(var i=0; i<ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1);  // strip leading spaces
    if (c.indexOf(name) != -1) {
      session_id = c.substring(name.length,c.length);
      break;
      };
    };
  document.cookie = "session_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC";
  //var randomnumber=Math.floor(Math.random()*11)  // from 0-10
  //Math.floor((Math.random()*100)+1); // from 1-100
  //Math.random().toString(36).substring(2, 9);  // from 2 to 8
  send_message('get_login', null, false);

  tick = setInterval(
    function() {send_message('send_req', [['tick', null]])},
      10000);  // send 'tick' every 10 seconds

  window.onbeforeunload = function() {
    return 'This will close the program. Are you sure?';
    };

  };
