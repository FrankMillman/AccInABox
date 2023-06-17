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
  // if focus not set on active form (most recent), reset on active form
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
  //   new_focus_form.disable_count + ' ' +
  //   (new_focus_form.current_focus === new_focus));

//  if (new_focus_form.disable_count) return;

  if (new_focus_form.root !== root_zindex[root_zindex.length-1]) {
    // focus set on non-active root - make it active
    var old_pos = new_focus_form.root.zindex;
    var new_pos = root_zindex.length-1;
    root_zindex.splice(new_pos, 0, root_zindex.splice(old_pos, 1)[0]);
    for (var i=old_pos; i<= new_pos; i++) {
      var root = root_zindex[i];
      root.zindex = i;
      for (var j=0, root_length=root.length; j<root_length; j++)
        root[j].style.zIndex = (i*100) + j;
      };
    };

  if (new_focus_form.current_focus === new_focus) {
    // can get here after errmsg box dismissed
    new_focus_form.focus_from_server = false;
    new_focus.frame.err_flag = false;
    return;
    };

  if (new_focus.disabled)
    return;  // opera accepts focus even if disabled!

  if (new_focus.tabIndex < 0)  // e.g. footer_row in grid - accept click, do not set focus
    return;

  //debug3('GOT FOCUS ' + new_focus.ref + ' ' + new_focus.help_msg + ' ' +
  //  (new_focus.frame.form.current_focus === new_focus) + ' ' +
  //  new_focus_form.focus_from_server);

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

// moved to after calling got_focus - implications? [2016-10-16]
    // why was this necessary? - there are implications!
    //  in AibDummy.prototype.after_got_focus, we check for
    //    (dummy.frame.form.current_focus === dummy), so if we set it after focus()
    //    it is too late
    // workaround [2016-11-20] -
    //   delay setting 'current_focus', but not 'setting_focus'
    // solves problem for now, but needs a proper solution
//  new_focus_form.current_focus = new_focus;
  new_focus_form.setting_focus = new_focus;  // IE workaround
//  if (new_focus_form.help_msg)
//    new_focus_form.help_msg.data = new_focus.help_msg;

  new_focus.got_focus();
  new_focus_form.focus_from_server = false;
  new_focus.frame.err_flag = false;

  new_focus_form.current_focus = new_focus;
//  new_focus_form.setting_focus = new_focus;  // IE workaround
  if (new_focus.help_msg)
    new_focus_form.help_msg.data = new_focus.help_msg;

  if (new_focus.active_frame !== new_focus.frame.form.active_frame) {

    var old_frame = new_focus.frame.form.active_frame;

    if (old_frame.default_button !== undefined)
      old_frame.default_button.style.border = '1px solid darkgrey';

    if (old_frame.type === 'grid_frame') {
      // clear border of current active_frame
      old_frame.page.style.border = '1px solid darkslategrey';
      old_frame.ctrl_grid.unhighlight_active_row();
      };

    new_focus.frame.form.active_frame = new_focus.active_frame;

    var new_frame = new_focus.active_frame;

    if (new_frame.default_button !== undefined)
      new_frame.default_button.style.border = '1px solid blue';

    if (new_frame.type === 'grid_frame') {
      new_frame.page.style.border = '1px solid blue';
      new_frame.ctrl_grid.highlight_active_row();
      };
    };
  };

function redisplay(args) {
  // debug3('redisp ' + JSON.stringify(args));
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
  // debug3('readonly ' + JSON.stringify(args));
  for (var i=0, l=args.length; i<l; i++) {
    var ref = args[i][0], state = args[i][1];
    var obj = get_obj(ref);
    //obj.readonly = state;
    obj.set_readonly(state);
    };
  };

function set_focus(args) {
  var obj_ref = args[0], err_flag=args[1];
  var obj = get_obj(obj_ref);
  obj.frame.form.focus_from_server = true;
  obj.frame.form.setting_focus = obj;  // IE workaround - delays actually setting focus!
  obj.frame.err_flag = err_flag;
  if (obj.nb_page !== null)
    // ensure object visible
    if (obj.nb_page.pos !== obj.nb_page.parentNode.current_pos)
      obj.nb_page.parentNode.req_new_page(obj.nb_page.pos, false)
  if (obj.has_focus)
    obj.got_focus()
  else
    obj.focus();
  };

function set_dflt(args) {
  // debug3('set_dflt ' + JSON.stringify(args));
  var obj = get_obj(args[0]), value = args[1];
  obj.set_dflt_val(value);
  };

function setup_choices(args) {
  var obj = get_obj(args[0]), choices = args[1];
  obj.aib_obj.setup_choices(obj, choices);
  };

function set_prev(args) {
  var obj = get_obj(args[0]);
  obj.aib_obj.set_prev_from_server(obj, args[1]);
  };

function cell_set_focus(args) {
  var grid_ref = args[0], row = args[1], col_ref = args[2], dflt_val=args[3], err_flag=args[4];
  var grid = get_obj(grid_ref);
  if (col_ref === null)
    var col = grid.active_col;
  else
    var col = get_obj(col_ref).col;

  // next block looks redundant, as it all happens in cell_set_focus() anyway
  // but there is an important difference [2017-11-20]
  // this way, grid.focus() is called *before* setting focus_from_server = true
  // this prevents grid.focus() trying to reset focus on the grid_frame, if there is one
  // don't know if this is by fluke or by design, but leaving it alone for now!

  if (!grid.has_focus) {
    // next lines added 2016-07-11
    // if current active_col has 'skip' set, we keep resetting focus on grid_frame :-(
    // this forces active_col to the column we are setting focus on
    // any implications?
    grid.active_col = col;
    if (grid.active_row === -1)  // added 2023-01-06
      grid.active_row = 0;
    grid.active_cell =
      grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[col];
    if (grid.active_row === grid.num_data_rows)
      grid.inserted = -1;
    else
      grid.inserted = 0;
    grid.focus();
    };

  grid.focus_from_server = true;
  grid.err_flag = err_flag;
  grid.cell_set_focus(row, col, dflt_val);
  };

// function render_bpmn(args) {
//   var svg = get_obj(args[0]), nodes = args[1], edges = args[2];
//   render_bpmn(svg, nodes, edges)
//   };

function start_frame(args) {
  var frame = get_obj(args[0]);
  var set_focus_ref = args[1];  // obj_ref to set focus on (or null)
  var obj_exists = args[2];  // does object exist?
  //debug3('start frame ' + frame.ref + ' focus=' + set_focus_ref);
  if (frame.combo_type !== undefined) {
    if (frame.combo_type === 'member')
      frame.tree.tree_frames['group'].page.style.display = 'none';
    else  // must be 'group'
      frame.tree.tree_frames['member'].page.style.display = 'none';
    frame.page.style.display = 'block';
    };
  frame.obj_exists = obj_exists;
  if (set_focus_ref !== null)
    set_focus([set_focus_ref, false]);
  };

function start_grid(args) {
  var grid = get_obj(args[0]);
  grid.start_grid(args[1]);
  };

function add_tree_data(args) {
  var tree_ref = args[0], tree_data = args[1], hide_root = args[2];
  var tree = get_obj(tree_ref);
  tree.add_tree_data(tree_data, hide_root);
  };

function recv_rows(args) {
  var grid = get_obj(args[0]);
  grid.recv_rows(args[1]);
  };

function append_row(args) {
  var grid = get_obj(args);
  grid.num_data_rows += 1;
  grid.append_row();
  if (grid.num_data_rows >= grid.num_grid_rows)
    grid.show_scrollbar();
  grid.draw_grid()
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
  var tree_ref=args[0], node_id=args[1], text=args[2], is_leaf=args[3];
  var tree = get_obj(tree_ref);
  tree.update_node(node_id, text, is_leaf);
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
  if (subtype._active_subtype !== subtype_id) {
    subtype[subtype._active_subtype].style.display = 'none';
    subtype[subtype_id].style.display = 'block';
    subtype._active_subtype = subtype_id;
    };
  };

function refresh_bpmn(args) {
  var svg_ref = args[0], nodes = args[1], edges = args[2];
  var svg = get_obj(svg_ref);
  render_bpmn(svg, nodes, edges);
  };

function append_tasks(args) {
  while (task_div.childNodes.length > 1)  // firstChild is 'task_hdng'
    task_div.removeChild(task_div.lastChild);
  for (var j=0; j<args.length; j++) {
    var task_row = document.createElement('div');
    task_row.task_id = args[j][0]
    task_div.appendChild(task_row);
    task_row.style.marginTop = '5px';
    task_row.style.marginLeft = '5px';
    // to prevent selection of text - IE only
    task_row.onselectstart = function() {return false};
    var text = document.createTextNode(args[j][1]);
    task_row.appendChild(text);
    task_row.onmouseover = function() {this.style.cursor = 'pointer'};
    task_row.onmouseleave = function() {this.style.cursor = 'default'};
    task_row.onclick = function() {
      var args = [this.task_id];
      send_request('claim_task', args);
      };
    };
  };

  function show_pdf(pdf_name) {
    // delay to allow onkeyup signal to be sent to correct window
    setTimeout(function() {window.open(pdf_name, '_blank')}, 150);
    };

  function get_csv(csv_name) {
    var link = document.createElement("a");
    // If you don't know the name or want to use the webserver default, set name = ''
    link.setAttribute('download', csv_name);
    link.href = csv_name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    };

function exception(args) {
  traceback = args.join('').replace(/\n/g, '<br>').replace(/ /g, '\xa0');  // replace all ' ' with &nbsp
  window.open('../error.html');  // it will read 'traceback' and display it
  clearInterval(tick);  // stop sending 'tick' to server
  };
