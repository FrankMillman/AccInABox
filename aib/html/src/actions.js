function close_program(args) {
  clearInterval(tick);
//  var d = new Date();
//  document.cookie = "sid=;expires=" + d.toGMTString() + ";" + ";";
//  setTimeout('self.close()', 0)
  };

function end_form(args) {
  var form = get_obj(args);
  form.close_form();
  };

function display_error(args) {
  var title = args[0];
  var message = args[1];
  // timeout needed to allow IE to finish setting focus on error field
  setTimeout(function() {show_errmsg(title, message)}, 0);
  };

function got_focus(new_focus) {
  // if focus not set on active form (most recent), reset on active_form
  var new_focus_form = new_focus.frame.form;
  var new_focus_root_forms = new_focus_form.root;
  if (new_focus_form !== new_focus_root_forms[new_focus_root_forms.length-1]) {
//    debug3('new_focus = ' + new_focus);
//    for (j=0; j<new_focus_root_forms.length; j++) {
//      debug3(j + ': ' + new_focus_root_forms[j]);
//      };
    new_focus = new_focus_root_forms[new_focus_root_forms.length-1].current_focus;
    if (new_focus !== null)
      new_focus.focus();
    return;
    };

  //debug3('GOT FOCUS ' + new_focus.ref + ' ' + new_focus.help_msg + ' ' +
  //   new_focus.frame.form.disable_count + ' ' +
  //   (new_focus.frame.form.current_focus === new_focus));

//  if (new_focus_form.disable_count) return;

  if (new_focus_form.current_focus === new_focus) {
    new_focus_form.focus_from_server = false;
    return;
    };
  if (new_focus.disabled)
    return;  // opera accepts focus even if disabled!

  //debug3('GOT FOCUS ' + new_focus.ref + ' ' + new_focus.help_msg + ' ' +
  //  (new_focus.frame.form.current_focus === new_focus) + ' ' +
  //  new_focus.frame.send_focus_msg);

  current_form = new_focus_form;  // global variable
  var old_focus = new_focus_form.current_focus;
  if (old_focus !== null) {
    var ok = old_focus.lost_focus();
    if (!ok) return;  // lost_focus failed validation (e.g. invalid date)
    // how do we reset focus back on the faulty field?
    // at present, we assume that 'errmsg' is called
    // when errmsg is closed, it resets focus on 'form.current_focus'
    // as this has not been updated (see next line) it sets it on the faulty field
    // a bit fragile!
    };
  new_focus_form.current_focus = new_focus;
  new_focus_form.setting_focus = new_focus;  // IE workaround
  if (new_focus_form.help_msg)
    new_focus_form.help_msg.data = new_focus.help_msg;

// if focus_from_server === true, should we call 'got_focus'?
// it sends 'got focus' back to the server, which we don't want
// change it and see what happens! [2013-08-23]

//  if (new_focus_form.focus_from_server)
//    new_focus_form.focus_from_server = false;
//  else
//    new_focus.got_focus();
  new_focus.got_focus();
  new_focus_form.focus_from_server = false;

  if (new_focus.active_frame !== new_focus.frame.form.active_frame) {

    var old_frame = new_focus.frame.form.active_frame;

    if (old_frame.default_button !== undefined)
      old_frame.default_button.style.border = '1px solid darkgrey';

    if (old_frame.type === 'grid_frame') {
      // clear border of current active_frame
      old_frame.page.style.border = '1px solid darkslategrey';
      //this.active_frame.ctrl_grid.parentNode.style.border = '1px solid transparent';
      old_frame.ctrl_grid.unhighlight_active_row();
      };

    new_focus.frame.form.active_frame = new_focus.active_frame;

    var new_frame = new_focus.active_frame;

    if (new_frame.default_button !== undefined)
      new_frame.default_button.style.border = '1px solid blue';

    if (new_frame.type === 'grid_frame') {
      new_frame.page.style.border = '1px solid blue';
      new_frame.ctrl_grid.highlight_active_row();
      new_frame.frame_amended = (new_frame.ctrl_grid.inserted !== 0);
      };
//
//    new_focus.frame.form.set_gridframe_border(new_focus.active_frame);
//    new_focus.frame.form.active_frame = new_focus.active_frame;
    };

  };

function redisplay(args) {
  for (var i=0, l=args.length; i<l; i++) {
    var ref = args[i][0], value = args[i][1];
    get_obj(ref).set_value_from_server(value);
    };
  };

function reset(args) {
  for (var i=0, l=args.length; i<l; i++) {
    var ref = args[i];
    get_obj(ref).reset_value();
    };
  };

function set_readonly(args) {
  for (var i=0, l=args.length; i<l; i++) {
    var ref = args[i][0], state = args[i][1];
    var obj = get_obj(ref);
//    if (state === false)
//      enable_obj(obj)
//    else
//      disable_obj(obj)
    obj.readonly = state;
    obj.set_readonly(state);
    };
  };

function enable_obj(obj) {
  obj.disable_count = 0;
  obj.set_disabled(false);
//  obj.disable_count -= 1;
//  if (!obj.disable_count) {
//    obj.set_disabled(false);
////    obj.disabled = false;
////    obj.tabIndex = 0;
//    };
  };

function disable_obj(obj) {
  obj.disable_count = 1;
  obj.set_disabled(true);
//  if (!obj.disable_count){
//    obj.set_disabled(true);
////    obj.disabled = true;
////    obj.tabIndex = -1;
////    if (obj === obj.frame.form.current_focus) {
////      var pos = obj.pos + 1;
////      while (obj.frame.obj_list[pos].disabled || obj.frame.obj_list[pos].display)
////        pos += 1;  // look for next enabled object
////      obj.frame.obj_list[pos].focus();
////      };
//    };
//  obj.disable_count += 1;
  };

function set_focus(args) {
  var obj = get_obj(args);
  obj.frame.form.focus_from_server = true;
  obj.frame.form.setting_focus = obj;  // IE workaround - delays actually setting focus!
  obj.focus();
  };

function recv_prev(args) {
  var obj = get_obj(args[0]);
  obj.aib_obj.set_prev_from_server(obj, args[1]);
  };

function cell_set_focus(args) {
  var grid_ref = args[0], row = args[1], col_ref = args[2], err_flag=args[3];
  var grid = get_obj(grid_ref);
  if (col_ref === null)
    var col = grid.active_col;
  else
    var col = get_obj(col_ref).col;
  if (!grid.has_focus)
    grid.focus();
  grid.focus_from_server = true;
  grid.err_flag = err_flag;
  grid.cell_set_focus(row, col);
  };

function start_frame(args) {
  var frame = get_obj(args[0]);
  frame.frame_amended = args[1];  // false if object exists, else true
  if (args[2]) {  // set_focus

    frame.form.tabdir = 1;  // in case 'dummy' gets focus
    for (var i=0, l=frame.obj_list.length; i<l; i++) {
      var obj = frame.obj_list[i];
      //if (obj.readonly || obj.display || !obj.offsetHeight)
      if (obj.display || !obj.offsetHeight)
        continue;  // look for the next obj
      else
        break;  // set focus on this obj
      };
    frame.form.focus_from_server = false;
    if (frame.form.current_focus === obj) {
      //obj.aib_obj.onfocus(obj);  // could be a grid - no aib_obj!

      // should we call obj.onfocus() or obj.got_focus()
      // if an input fld, onfocus() calls aib_obj.onfocus(), which
      //   hides/shows dsp/inp as appropriate, then calls global got_focus()
      // if a grid, onfocus() just calls global got_focus()
      // global got_focus() checks if the object already has focus
      // if it does not, it calls object.got_focus()
      // for now, call both!

      obj.onfocus();
      obj.got_focus();
      }
    else {
//      if (frame.form.current_focus !== null)
      if (frame.type === 'frame') // don't do this for grid_frame
        frame.send_focus_msg = false;  // do not notify server of 'lost/got_focus'
      setTimeout(function() {obj.focus()}, 0);
      };
    };
  };

function start_grid(args) {
  var grid = get_obj(args[0]);
  grid.start_grid(args[1]);
  };

function recv_rows(args) {
  var grid = get_obj(args[0]);
  grid.recv_rows(args[1]);
  };

function move_row(args) {
  var grid = get_obj(args[0]);
  grid.move_row(args[1], args[2]);
  };

function insert_row(args) {
  var grid = get_obj(args[0]);
  grid.insert_row(args[1]);
  };

function delete_row(args) {
  var grid = get_obj(args[0]);
  grid.delete_row(args[1]);
  };

function insert_node(args) {
  var tree_ref=args[0], parent_id=args[1], seq=args[2], node_id=args[3];
  var tree = get_obj(tree_ref);
  tree.insert_node(parent_id, seq, node_id);
  };

function update_node(args) {
  var tree_ref=args[0], node_id=args[1], text=args[2], expandable=args[3];
  var tree = get_obj(tree_ref);
  tree.update_node(node_id, text, expandable);
  };

function delete_node(args) {
  var tree_ref=args[0], node_id=args[1];
  var tree = get_obj(tree_ref);
  tree.delete_node(node_id);
  };

function set_subtype(args) {
  var frame_ref = args[0], subtype_name = args[1], subtype_id = args[2];
  var frame = get_obj(frame_ref);
  var subtype = frame.subtypes[subtype_name];
  subtype[subtype._active_box].style.display = 'none';
  subtype[subtype_id].style.display = 'block';
  subtype._active_box = subtype_id;
  };

function exception(args) {
  //document.body.innerHTML =
  //  args.join('<br>').replace(/ /g, '\xa0');  // replace all ' ' with &nbsp;
  //debug3(
  //  args.join('<br>').replace(/ /g, '\xa0'));  // replace all ' ' with &nbsp;

  traceback = args.join('<br>').replace(/ /g, '\xa0');
  window.open('../error.html');  // it will read 'traceback' and display it

  clearInterval(tick);  // stop sending 'tick' to server
  };
