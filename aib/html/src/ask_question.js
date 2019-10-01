function ask_question(args) {
  var frame_ref = args[0];
  question.caption.data = args[1];  // title
  //question.text.innerHTML = args[2];  // question
  question.text.data = args[2];  // question
  var answers = args[3];
  var dflt = args[4];
  question.escape = args[5];
  question.callback = args[6];

  document.body.appendChild(question);
  question.style.display = 'block';

  question.close_window = function(answer) {
    question.removeChild(button_row);
    question.style.display = 'none';
    question.style.width = '';
    document.body.removeChild(question);
    current_form = question.active_form;
    current_form.enable_controls();
    current_form.current_focus.focus();
    if (frame_ref !== null) {
      var args = [frame_ref, answer];
      send_request('answer', args);
      }
    else {
      var callback = question.callback;
      var ctx = callback[0];
      var func = callback[1];
      func.call(ctx, answer);
      };
    };

  var button_row = document.createElement('div');
  button_row.style.padding = '5px 0px 10px';  // top l/r bot
  button_row.style.textAlign = 'center';
  question.appendChild(button_row);

  for (var i=0; i<answers.length; i++) {
    var ans = answers[i];
    var button = document.createElement('button');
    button.style.textAlign = 'center';
    button.style.marginLeft = '10px';
    button.style.marginRight = '10px';
    button.label = ans;
    button.appendChild(document.createTextNode(ans));

    button.style.border = '1px solid darkgrey';
    button.style.color = 'navy';
    button.style.outline = '0px solid transparent';
    button.style.height = '22px';
    button.style.borderRadius = '4px';


    button.onclick = function(e) {
      // FF sometimes generates click event when Enter pressed
      // this ensures that clicked() only gets called once
      if (!click_from_kbd)
        this.clicked();
      };

    button.clicked = function() {question.close_window(this.label)};
    button.pos = button_row.childNodes.length;
    if (ans === dflt) {
      question.dflt_pos = button.pos;
      button.style.border = '1px solid blue';
      }
    button_row.appendChild(button);
    if (button.offsetWidth < 60)
      button.style.width = '60px';
    };

  if (question.offsetWidth < 200)
    question.style.width = '200px';
  var max_x = (max_w - question.offsetWidth);
  var max_y = (max_h - question.offsetHeight);
  question.style.left = (max_x / 2) + 'px';
  question.style.top = (max_y / 4) + 'px';

  current_form.disable_controls();
  question.active_form = current_form;
  question.current_focus = question.lastChild.childNodes[question.dflt_pos];

  Drag.init(question.header, question, 0, max_x, 0, max_y);
  question.onDragEnd = function(x, y) {
    question.current_focus.focus();
    };

  question.current_focus.focus();
  current_form = question

  question.style.zIndex = root_zindex.length * 100
  };

question = document.createElement('div');
question.style.position = 'absolute';
question.style.border = '2px solid green';
question.style.background = 'white';

var header = document.createElement('div');
header.form = question;
header.style.background = 'palegreen';
header.style.fontWeight = 'bold';
header.style.paddingLeft = '5px';
header.style.borderBottom = '1px solid green';
header.style.cursor = 'default';
var caption = document.createTextNode('');
question.caption = caption;
header.appendChild(caption);
// to prevent selection of text - IE only
header.onselectstart = function(){return false};
question.header = header;
question.appendChild(header);

var question_text = document.createElement('div');
//question.text = question_text;
//question_text.style.fontSize = '80%';
question_text.style.padding = '25px';
question_text.style.textAlign = 'center';
//question.style.overflow = 'hidden';
question.style.wordWrap = 'break-word';
question.style.whiteSpace = 'pre';
question.appendChild(question_text);
question_text.appendChild(document.createTextNode(''));
question.text = question_text.firstChild;

question.onkeydown = function(e) {
  if (!e) e=window.event;
  switch (e.keyCode) {
    case 27: {  // Esc
      this.close_window(this.escape);
      break;
      };
    case 37: {  // Left
      if (this.dflt_pos > 0) {
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid darkgrey';
        this.dflt_pos -= 1;
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid blue';
        this.current_focus.focus();
        };
      break;
      };
    case 38: {  // Up
      if (this.dflt_pos > 0) {
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid darkgrey';
        this.dflt_pos -= 1;
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid blue';
        this.current_focus.focus();
        };
      break;
      };
    case 39: {  // Right
      if (this.dflt_pos < (this.lastChild.childNodes.length-1)) {
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid darkgrey';
        this.dflt_pos += 1;
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid blue';
        this.current_focus.focus();
        };
      break;
      };
    case 40: {  // Down
      if (this.dflt_pos < (this.lastChild.childNodes.length-1)) {
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid darkgrey';
        this.dflt_pos += 1;
        this.current_focus = this.lastChild.childNodes[this.dflt_pos];
        this.current_focus.style.border = '1px solid blue';
        this.current_focus.focus();
        };
      break;
      };
    };
  };

question.style.display = 'none';
