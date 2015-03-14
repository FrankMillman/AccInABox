function show_cal(parent, current_value, callback) {

  document.body.appendChild(calendar);
  calendar.style.display = 'block';

  var max_x = (max_w - calendar.offsetWidth);
  var max_y = (max_h - calendar.offsetHeight);
  calendar.style.left = (max_x / 2) + 'px';
  calendar.style.top = (max_y / 4) + 'px';

  Drag.init(calendar.header, calendar, 0, max_x, 0, max_y);
  calendar.onDragEnd = function(x, y) {
    calendar.current_focus.focus();
    };

  current_form.disable_controls();
  var root_id = current_form.root_id;
  var form_id = current_form.form_id;
  var root = active_roots[root_id];
  calendar.root_id = root_id;
  calendar.form_id = (form_id + 1);
  calendar.root = root;
  root.push(calendar);
  calendar.style.zIndex = (root.zindex*100) + root.length;
  calendar.save_current_form = current_form;
  calendar.current_focus = calendar.page;
  current_form = calendar;
  calendar.parent = parent;
  calendar.callback = callback;

  if (current_value === '')
    var date = new Date();
  else {
    var dt = current_value.split('-');
    var date = new Date(dt[0], dt[1]-1, dt[2]);
    }
  calendar.current_year = date.getFullYear();
  calendar.current_month = date.getMonth();
  calendar.current_day = date.getDate();
  var dates = calendar.get_dates(date);
  for (var i=0; i<42; i++) {
    var dd = calendar.page.childNodes[i];
    dd.innerHTML = dates[i];
    if (dates[i] == calendar.current_day) {
      dd.style.background = 'darkblue';
      dd.style.color = 'white';
      };
    };

  calendar.style.zIndex = root_zindex.length * 100

  //calendar.obj_list[0].set_value_from_server(calendar.current_month);
  calendar.data_mth.set_value_from_server(calendar.current_month);
  //calendar.obj_list[1].set_value_from_server(calendar.current_year);
  calendar.data_yr.set_value_from_server(calendar.current_year);

  setTimeout(function() {calendar.page.focus()}, 0);

  };

calendar = document.createElement('div');
calendar.style.fontFamily= 'arial, verdana, helvetica, sans-serif';
calendar.style.fontSize = '10pt';
calendar.style.position = 'absolute';
calendar.style.background = 'white';
calendar.style.border = '1px solid black';

calendar.internal = true;  // do not send 'change_focus' events

var header = document.createElement('div');
header.form = calendar;
header.style.background = 'darkblue';
header.style.color = 'white';
header.style.fontWeight = 'bold';
header.style.paddingLeft = '5px';
header.style.cursor = 'default';
header.innerHTML = 'Calendar';
// to prevent selection of text - IE only
header.onselectstart = function(){return false};
calendar.header = header;
calendar.appendChild(header);

var month = document.createElement('div');
calendar.appendChild(month);
month.style.margin = '5px';
month.style.padding = '2px';
month.style.border = '1px solid black';

calendar.focus_from_server = false;
calendar.disable_count = 0;
//calendar.obj_list = [];

var frame = {}  // new Object()
frame.obj_list = [];
frame.form = calendar;
frame.form.obj_dict = {};
frame._amended = false;
calendar.active_frame = frame;

calendar.get_dates = function(date) {
  // first_day and last_day are not equivalent!
  // first_day is the day of the week (0-6) of the 1st of the month
  // last_day is the actual last day of the month

  calendar.first_day = ((date.getDay() - date.getDate()) % 7);
  if (calendar.first_day < 0) calendar.first_day += 7;

  calendar.last_day = new Date(date.getFullYear(), date.getMonth()+1, 0).getDate();

  var dates = [];
  for (var i=0; i<42; i++) {
    if (i < calendar.first_day)
      dates.push('')
    else if (i >= (calendar.last_day + calendar.first_day))
      dates.push('')
    else
      dates.push((i - calendar.first_day + 1))
    };
  return dates;
  };

calendar.onchange_yr = function(option_selected) {
  if (option_selected != calendar.current_year) {
    var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
    dd.style.background = 'white';
    dd.style.color = 'black';
    calendar.current_year = option_selected;
    var date = new Date(calendar.current_year, calendar.current_month, 1);
    var dates = calendar.get_dates(date);
    for (var i=0; i<42; i++) {
      var dd = calendar.page.childNodes[i];
      dd.innerHTML = dates[i];
      };
    if (calendar.current_day > calendar.last_day)
      calendar.current_day = calendar.last_day;
    var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
    dd.style.background = 'grey';
    dd.style.color = 'white';
    };
  };

calendar.onchange_mth = function(option_selected) {
  if (calendar.current_month === undefined) return;
  if (option_selected != calendar.current_month) {
    var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
    dd.style.background = 'white';
    dd.style.color = 'black';
    calendar.current_month = option_selected;
    var date = new Date(calendar.current_year, calendar.current_month, 1);
    var dates = calendar.get_dates(date);
    for (var i=0; i<42; i++) {
      var dd = calendar.page.childNodes[i];
      dd.innerHTML = dates[i];
      };
    // TODO
    // the next lines cater for current_day == 31, but last_day == 30
    // it works, but it would be nice to revert to 31 if possible on the next change
    // at present we have lost that information, so cannot be done
    if (calendar.current_day > calendar.last_day)
      calendar.current_day = calendar.last_day;
    var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
    dd.style.background = 'grey';
    dd.style.color = 'white';
    };
  // timeout 50 - wait for 'choice' to get focus, then move focus to 'page'
  // timeout 0 - set focus to 'page', then reset focus back to 'choice'
  // 0 is preferable, otherwise you cannot move up/down with arrow keys
  //   to select calendar month - it keeps setting focus back to page!
  setTimeout(function() {page.focus()}, 0);
  };

calendar.onchange_day = function(option_selected) {
  if (option_selected != calendar.current_day) {
    var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
    dd.style.background = 'white';
    dd.style.color = 'black';
    calendar.current_day = option_selected;
    var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
    dd.style.background = 'darkblue';
    dd.style.color = 'white';
    };
  };

var data_row = document.createElement('div');
data_row.style.marginTop = '10px';
data_row.style.height = '21px';

var args = {};  //new Object();
args.type = 'choice';
args.ref = '0';
args.lng = 40;
args.value = 0;
args.help_msg = 'Month';
args.readonly = false;
args.amend_ok = true;
args.allow_amend = true;
var choices = [[0, 'Jan'], [1, 'Feb'], [2, 'Mar'], [3, 'Apr'], [4, 'May'], [5, 'Jun'],
  [6, 'Jul'], [7, 'Aug'], [8, 'Sep'], [9, 'Oct'], [10, 'Nov'], [11, 'Dec']];
args.choices = [null, choices];
args.callback = calendar.onchange_mth;

var data_mth = create_input(frame, args);
//data_mth.choice.onfocus = function() {data_mth.choice.after_got_focus()};
data_mth.style.marginLeft = '20px';
data_row.appendChild(data_mth);
calendar.data_mth = data_mth.childNodes[0];

var args = {};  //new Object();
args.type = 'spin';
args.ref = '1';
args.lng = 40;
args.value = 0;
args.help_msg = 'Year';
args.readonly = false;
args.amend_ok = true;
args.allow_amend = true;
args.min = 1900;
args.max = 2100;
args.callback = calendar.onchange_yr;

var data_yr = create_input(frame, args);
//data_yr.spin.onfocus = function() {data_yr.spin.after_got_focus()};
data_yr.style.marginLeft = '30px';
data_row.appendChild(data_yr);
calendar.data_yr = data_yr.childNodes[0];

month.appendChild(data_row);

var page_width = 210;
var dd_width = page_width / 7;
month.style.width = page_width + 'px';

var days = document.createElement('div');
days.style.marginTop = '5px';
for (var i=0; i<7; i++) {
  var dd = document.createElement('span');
  dd.style.display = 'inline-block';
  dd.style.width = dd_width + 'px';
  dd.style.height = '18px';
  dd.style.paddingTop = '2px';
  dd.style.background = 'white';
  dd.style.marginTop = '2px';
  dd.style.fontFamily= 'arial, verdana, helvetica, sans-serif';
  dd.style.fontSize = '8pt';
  dd.style.textAlign = 'center';
  dd.innerHTML = ['M', 'T', 'W', 'T', 'F', 'S', 'S'][i];
  days.appendChild(dd);
  };
month.appendChild(days);

var page = document.createElement('div');
month.appendChild(page);
calendar.page = page;
page.form = calendar;
page.frame = frame;
page.active_frame = frame;
page.help_msg = 'Page';
page.tabIndex = 0;
page.style.height = '126px';
page.style.width = page_width + 'px';
page.style.borderTop = '1px solid grey';
page.style.borderBottom = '1px solid grey';
page.style.outline = '0px solid transparent';  // suppress outline on focus

page.ref = '2';
page.pos = frame.obj_list.length;
frame.obj_list.push(page);
frame.form.obj_dict[page.ref] = page;

for (var i=0; i<42; i++) {
  var dd = document.createElement('div');
  dd.style[cssFloat] = 'left';
  dd.style.width = dd_width + 'px';
  dd.style.height = '18px';
  dd.style.paddingTop = '3px';
  dd.style.background = 'white';
  dd.style.fontFamily= 'arial, verdana, helvetica, sans-serif';
  dd.style.fontSize = '8pt';
  dd.style.textAlign = 'center';
  dd.style.cursor ='default';
  dd.onclick = function(e) {
    if (this.innerHTML != '&nbsp;')
      calendar.onchange_day(+this.innerHTML);
    };
  page.appendChild(dd);
  };

page.onfocus = function(e) {got_focus(page)};

page.got_focus = function() {
  var dd = page.childNodes[calendar.current_day+calendar.first_day-1];
  dd.style.background = 'darkblue';
  dd.style.color = 'white';
  };

page.lost_focus = function() {
  var dd = page.childNodes[calendar.current_day+calendar.first_day-1];
  dd.style.background = 'grey';
  dd.style.color = 'white';
  return true;
  };

page.onkey = function(e) {
  if (!e) e=window.event;
  if (e.altKey || e.ctrlKey)
    return;
  if (e.keyCode == 9)  // tab
    return;
  var current_day = calendar.current_day;
  if (e.keyCode == 13) { // Enter
    var new_date = new Date(calendar.current_year, calendar.current_month, calendar.current_day);
    calendar.close_window(new_date);
    }
  else if (e.keyCode == 27) { // Escape
    var new_date = null;
    calendar.close_window(new_date);
    }
  else if (e.keyCode == 37) {  // left
    if (calendar.current_day > 1)
      calendar.onchange_day(calendar.current_day-1);
    }
  else if (e.keyCode == 38) {  // up
    if (calendar.current_day > 7)
      calendar.onchange_day(calendar.current_day-7);
    }
  else if (e.keyCode == 39) {  // right
    if (calendar.current_day < calendar.last_day)
      calendar.onchange_day(calendar.current_day+1);
    }
  else if (e.keyCode == 40) {  // down
    if (calendar.current_day < (calendar.last_day-6))
      calendar.onchange_day(calendar.current_day+7);
    }
  else if (e.keyCode == 36) {  // home
    if (calendar.current_day > 1)
      calendar.onchange_day(1);
    }
  else if (e.keyCode == 35) {  // end
    if (calendar.current_day < calendar.last_day)
      calendar.onchange_day(calendar.last_day);
    };
  e.cancelBubble = true;
  return false;
  };

if (navigator.appName == 'Opera')
  page.onkeypress = page.onkey
else
  page.onkeydown = page.onkey;

var button_row = document.createElement('div');
button_row.style.padding = '10px';
button_row.style.textAlign = 'center';
month.appendChild(button_row);

var btn_ok = document.createElement('button');
button_row.appendChild(btn_ok);
btn_ok.style.textAlign = 'center';
btn_ok.style.margin = '0px 10px';
btn_ok.appendChild(document.createTextNode('Ok'));
if (btn_ok.offsetWidth < 60)
  btn_ok.style.width = '60px';
btn_ok.onclick = function() {
  var new_date = new Date(calendar.current_year, calendar.current_month, calendar.current_day);
  calendar.close_window(new_date);
  };

var btn_cancel = document.createElement('button');
button_row.appendChild(btn_cancel);
btn_cancel.style.textAlign = 'center';
btn_cancel.style.margin = '0px 10px';
btn_cancel.appendChild(document.createTextNode('Cancel'));
if (btn_cancel.offsetWidth < 60)
  btn_cancel.style.width = '60px';
btn_cancel.onclick = function() {
  var new_date = null;
  calendar.close_window(new_date);
  };

calendar.req_cancel = function() {
  var new_date = null;
  calendar.close_window(new_date);
  };

calendar.close_window = function(new_date) {
  //var choice = calendar.childNodes[1].childNodes[0].childNodes[0];
  //var choice = calendar.obj_list[0];
  //choice.aib_obj.close_dropdown(choice);
  calendar.data_mth.aib_obj.close_dropdown(calendar.data_mth);
  //if (new_date != null)
  //  calendar.parent.current_value = new_date;
  var dd = calendar.page.childNodes[calendar.current_day+calendar.first_day-1];
  dd.style.background = 'white';
  dd.style.color = 'black';
  document.body.removeChild(calendar);
  this.root.splice(this.root.length-1, 1);  // remove last entry
  //calendar.current_focus.has_focus = false;
  current_form = calendar.save_current_form;
  current_form.enable_controls();
  //calendar.parent.aib_obj.after_got_focus(calendar.parent);
  //setTimeout(function() {calendar.parent.focus()}, 0);

  if (new_date !== null)
    new_date = new_date.getFullYear() + '-' +
      zfill(new_date.getMonth()+1, 2) + '-' + zfill(new_date.getDate(), 2);

  calendar.callback(calendar.parent, new_date);
  };
