dbg = false;  // debug flag

if (window.innerWidth) {  // ff etc
  max_w = window.innerWidth;
  max_h = window.innerHeight;
  }
else {  // msie
  max_w = document.documentElement.clientWidth-20;
  max_h = document.documentElement.clientHeight;
  };

if (document.body.style.cssFloat === undefined)
  cssFloat = 'styleFloat';  // IE
else
  cssFloat = 'cssFloat';  // standard

// IE8 does not have Array.indexOf() - this adds it
if (!Array.prototype.indexOf) {
  Array.prototype.indexOf = function(elem) {
    for (var pos=0, len=this.length; pos<len; pos++)
      if (this[pos] === elem)
        return pos;
    return -1;
    };
  };
if (!Array.prototype.lastIndexOf) {
  Array.prototype.lastIndexOf = function(elem) {
    var pos = this.length;
    while (pos--)
      if (this[pos] === elem)
        return pos;
    return -1;
    };
  };

/* not using this at the moment (25/07/2012) but worth keeping
// check if we are using Explorer Canvas
EX = (navigator.appName === 'Microsoft Internet Explorer') &&
    (+navigator.userAgent.match(/MSIE ([\d.]+)?/)[1] < 9);
*/

function getCSSClass_string(css_class) {  // IE8
  // if css_class exists in styleSheet, return it
  for (var i=0; i<styleSheet.rules.length; i++) {
    rule = styleSheet.rules[i];
    if (rule.selectorText === '.' + css_class)
      return rule;
    };
  // we only get here if css_class does not exist
  // create new empty css_class and return it
  styleSheet.addRule('.' + css_class, null);
  rule = styleSheet.rules[styleSheet.rules.length-1];
  return rule;
  };

function getCSSClass_object(css_class) {  // the rest
  // if css_class exists in styleSheet, return it
  for (var i=0; i<styleSheet.cssRules.length; i++) {
    rule = styleSheet.cssRules[i];
    if (rule.selectorText === '.' + css_class)
      return rule;
    };
  // we only get here if css_class does not exist
  // create new empty css_class and return it
  styleSheet.insertRule('.' + css_class + "{ }", 0);
  rule = styleSheet.cssRules[0];
  return rule;
  };

function delCSSClass_string(css_class) {  // IE8
  // if css_class exists in styleSheet, delete it
  for (var i=0; i<styleSheet.rules.length; i++) {
    rule = styleSheet.rules[i];
    if (rule.selectorText === '.' + css_class) {
      styleSheet.removeRule(i);
      break;
      };
    };
  };

function delCSSClass_object(css_class) {  // the rest
  // if css_class exists in styleSheet, delete it
  for (var i=0; i<styleSheet.cssRules.length; i++) {
    rule = styleSheet.cssRules[i];
    if (rule.selectorText === '.' + css_class) {
      styleSheet.deleteRule(i);
      break;
      };
    };
  };

// search for active styleSheet
styleSheet = null;  // global
var media, mediaType;
if (document.styleSheets.length > 0) {
  for (var i=0; i<document.styleSheets.length; i++) {
    if (document.styleSheets[i].disabled)
      continue;
    media = document.styleSheets[i].media;
    mediaType = typeof media;
    if(mediaType === "string") {  // IE8
      if (media === "" || (media.indexOf("screen") !== -1))
        styleSheet = document.styleSheets[i];
      }
    else if(mediaType === "object") {  // the rest
      if(media.mediaText === "" || (media.mediaText.indexOf("screen") !== -1))
        styleSheet = document.styleSheets[i];
      };
    if (styleSheet !== undefined)
      break;
    };
  };
// if not found, create new styleSheet
if (styleSheet === null) {
  var styleSheetElement = document.createElement("style");
  styleSheetElement.type = "text/css";
  document.getElementsByTagName("head")[0].appendChild(styleSheetElement);
  for (var i=0; i<document.styleSheets.length; i++) {
    if (document.styleSheets[i].disabled)
      continue;
    styleSheet = document.styleSheets[i];
    break;
    };
  media = styleSheet.media;
  mediaType = typeof media;
  };
// set up global names for get/del CSSClass functions
if (mediaType === "string") {  // IE8
  getCSSClass = getCSSClass_string
  delCSSClass = delCSSClass_string
  }
else if (mediaType === "object") {  // the rest
  getCSSClass = getCSSClass_object
  delCSSClass = delCSSClass_object
  };

debug_setup = false;
function setup_debug () {
  var debug_row = document.createElement('div');
  debug_row.id = 'debug';
  document.body.appendChild(debug_row);
  // debug4 is to handle Opera bug - remove when fixed
  // also handles IE bug - form_setup_gui too narrow - this fixes it! [2014-07-24]
  var debug_4 = document.createElement('div');
  debug_4.id = 'debug4';
  debug_4.style.display = 'none';
  document.body.appendChild(debug_4);
  debug_setup = true;
  };

str = new String();
function debug(msg) {
  if (!debug_setup) setup_debug();
  if (str.length) str += '<br>';
  str += msg;
  document.getElementById('debug').innerHTML = str;
  };

function debug2(msg) {
  document.getElementById('debug2').innerHTML = msg;
  };

/*
str3 = ''  //new String();
function debug3(msg) {
  if (str3.length) str3 += '<br>';
  str3 += msg;
  document.getElementById('debug3').innerHTML = str3;
  };
*/

//str3 = [];  //new Array();
str3 = new String();
function debug3(msg) {
//  str3.push(msg);
//  if (str3.length > 32)
//    str3.shift();
//  document.getElementById('debug3').innerHTML = str3.join('<br>');
//  if (str3.length) str3 += '<br>';
//  str3 += msg;
  if (str3.length) str3 = '<br>' + str3;
  str3 = msg + str3;
  document.getElementById('debug3').innerHTML = str3;
  //var dbg = document.getElementById('debug3')
  //dbg.innerHTML = str3;
  //dbg.scrollTop = dbg.scrollHeight;  // force scroll to bottom
  };

// debug4 is to handle Opera bug - remove when fixed
// also handles IE bug - form_setup_gui too narrow - this fixes it! [2014-07-24]
function debug4(msg) {
  if (!debug_setup) setup_debug();
  document.getElementById('debug4').innerHTML = msg;
  };

function new_canvas(width, height, parent) {
  var canvas = document.createElement('canvas');
  parent.appendChild(canvas);
  if (typeof(G_vmlCanvasManager) != 'undefined')
    G_vmlCanvasManager.initElement(canvas);  // IE only
  canvas.width = width;
  canvas.height = height;
  return canvas;
  };

function setInsertionPoint(elem, start, end) {
  if (end === undefined) end = start;
  if (elem.setSelectionRange) {
    elem.setSelectionRange(start, end);
    }
  else if (elem.createTextRange) {
    var range = elem.createTextRange();
    if (start === end) range.collapse(true);
    range.moveEnd('character', end);
    range.moveStart('character', start);
    range.select();
    };
  };

function getCaret(elem) {
  if (elem.selectionStart)
    return elem.selectionStart;
  if (document.selection) {
    elem.focus();
    var r = document.selection.createRange();
    if (r === null) {
      return 0;
      }
    var re = elem.createTextRange(), rc = re.duplicate();
    re.moveToBookmark(r.getBookmark());
    rc.setEndPoint('EndToStart', re);
    return rc.text.length;
    }
  return 0;
  }

function find_pos(elem) {
  var x = y = 0;
  do {
    x += elem.offsetLeft;
    y += elem.offsetTop;
    } while (elem = elem.offsetParent);  // assign to 'elem', then test
  return [x, y];
  };

function zfill(n, w){
  var pad = new Array(1+w).join('0');
  return (pad+n).slice(-pad.length);
  };

function html_esc(s) {
  // this works, but the other one is easier to understand
  //var pre = document.createElement('pre');
  //var text = document.createTextNode(s);
  //pre.appendChild(text);
  //return pre.innerHTML;
  return s
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
  };

function get_obj(ref) {
  var ref_list = ref.split('_');
  var root = active_roots[ref_list.shift()];  // pop first element
  var form = root[ref_list.shift()];  // pop first element
  if (!ref_list.length)  // must be a 'form' ref
    return form;
  return form.obj_dict[ref];
  };

callbacks = [];
function exec_callbacks() {
//  if (callbacks.length)
//    debug3('CALLBACK ' + callbacks[0][0]);
  while (callbacks.length) {
    callback = callbacks.pop();
    var ctx = callback.shift();  // shift removes and returns first element
    var func = callback.shift();  // callback now contains arguments
    func.apply(ctx, callback);
    };
  };

//function exec_callback() {
//  callback = callbacks.pop();
//  var ctx = callback.shift();  // shift removes first element
//  var func = callback.shift();  // callback now contains arguments
//  func.apply(ctx, callback);
//  };

requests = [];
function send_request(event_id, args) {
  if (dbg)
    debug3('<- ' + requests.length + ' ' + event_id + ' ' + JSON.stringify(args));
  if (!requests.length)  // only do this once - first time
    setTimeout(function() {send_requests()}, 0);
  requests.push([event_id, args]);
  };

function send_requests() {
  send_message('send_req', requests);
  requests = [];
  };

function send_message(url, message) {
  var xmlhttp=new XMLHttpRequest();

  xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState==4 && xmlhttp.status==200)
      process_response(xmlhttp.responseText);
    };

  //var rnd = Math.random();
  //var msg = url + '?' + JSON.stringify([session_id, message, rnd]);
  //xmlhttp.open('GET', msg, true);
  //xmlhttp.send(null);
  xmlhttp.open('POST', url, true);
  xmlhttp.send(JSON.stringify([session_id, message]));
  };

function process_response(response_text) {
  var callback_blocked = false;

  if (response_text.length) {
    var response = JSON.parse(response_text);
    for (var i=0, l=response.length; i<l; i++) {
      var msg = response[i];
      var msg_type = msg[0];
      var msg_args = msg[1];
      // debug3('msg ' + msg_type);
      if (dbg)
        if (
            ['setup_form', 'start_menu', 'start_grid', 'recv_rows', 'redisplay']
            .indexOf(msg_type) !== -1)
          debug3('-> ' + i + ' ' + msg_type)
        else
          debug3('-> ' + i + ' ' + msg_type + ' ' + JSON.stringify(msg_args));
      switch(msg_type) {
        case 'ask_question': ask_question(msg_args); callback_blocked = true; break;
        case 'close_program': close_program(msg_args); break;
        case 'display_error': display_error(msg_args); break;
        case 'end_form': end_form(msg_args); break;
        case 'redisplay': redisplay(msg_args); break;
        case 'reset': reset(msg_args); break;
        case 'set_focus': set_focus(msg_args); break;
        case 'set_readonly': set_readonly(msg_args); break;
        case 'setup_form': setup_form(msg_args); break;
        case 'refresh_bpmn': refresh_bpmn(msg_args); break;
        case 'start_frame': start_frame(msg_args); break;
        case 'start_menu': start_menu(msg_args); break;
        case 'start_grid': start_grid(msg_args); break;
        case 'add_tree_data': add_tree_data(msg_args); break;
        case 'set_dflt': set_dflt(msg_args); break;
        case 'setup_choices': setup_choices(msg_args); break;
        case 'set_prev': set_prev(msg_args); break;
        case 'recv_rows': recv_rows(msg_args); break;
        case 'cell_set_focus': cell_set_focus(msg_args); break;
        case 'append_row': append_row(msg_args); break;
        case 'move_row': move_row(msg_args); break;
        case 'insert_row': insert_row(msg_args); break;
        case 'delete_row': delete_row(msg_args); break;
        case 'insert_node': insert_node(msg_args); break;
        case 'update_node': update_node(msg_args); break;
        case 'delete_node': delete_node(msg_args); break;
        case 'set_subtype': set_subtype(msg_args); break;
        case 'append_tasks': append_tasks(msg_args); break;
        case 'show_pdf': show_pdf(msg_args); break;
        case 'get_csv': get_csv(msg_args); break;
        case 'exception': exception(msg_args); break;
        default: debug3('UNKNOWN ' + msg_type + ': ' + msg_args);
        };
      };
    };
  if (callbacks.length)
    if (!callback_blocked)
      exec_callbacks();
  };
