function create_grid(frame, main_grid, page, json_elem, col_defns) {

  var grid = document.createElement('div');
  grid.style.outline = 'none';  // disable highlight on focus
//  grid.style.border = '1px solid lightgrey';
  grid.style[cssFloat] = 'left';  // in case we add a scrollbar
  main_grid.appendChild(grid);
  main_grid.grid = grid;

  grid.pos = frame.obj_list.length;
  frame.obj_list.push(grid);
  frame.form.obj_dict[json_elem.ref] = grid;
  grid.frame = frame;
  grid.nb_page = page.nb_page;
  grid.active_frame = frame;  // can be over-ridden by grid_frame
  grid.ref = json_elem.ref;
  grid.growable = json_elem.growable;
  grid.readonly = json_elem.readonly;
  grid.auto_startrow = json_elem.auto_startrow;
  grid.expand_col = json_elem.expand_col;
  grid.num_grid_rows = json_elem.num_grid_rows;
  grid.header_row = json_elem.header_row;
  grid.footer_row = json_elem.footer_row;
  grid.has_focus = false;
  grid.clicked = false;
  grid.start_in_progress = false;
  grid.inserted = 0;  // 0=existing row  -1=appended row  1=inserted row
  grid._amended = false;
  grid.num_cols = col_defns.length;
  grid.row_count = null;
  grid.form_row_count = null;
  grid.help_msg = '';
  grid.scrollbar_setup = false;
  grid.edit_in_progress = false;
  grid.tabbing = false;
  grid.grid_frame = null;
  grid.req_save_row = false;
  grid.kbd_shortcuts = {};
  grid.kbd_shortcuts['normal'] = {};
  grid.kbd_shortcuts['alt'] = {};
  grid.kbd_shortcuts['ctrl'] = {};
  grid.kbd_shortcuts['shift'] = {};

  grid.highlighted_cell = null;
  grid.highlighted_row = null;
  grid.active_cell = null;
  grid.active_row = -1;
  grid.active_col = -1;

//  // next 5 can be over-ridden by toolbar options
//  grid.insert_ok = false;
//  grid.delete_ok = false;
//  grid.formview_ok = false;
//  grid.navigate_ok = false;
//  grid.lkup_select_ok = false;

  grid.tabIndex = 0;  // so that it will accept 'focus'
//  grid.grid_width = 0;
  grid.grid_height = 0;

  grid.obj_list = [];

  // set up headings
  var grid_head = document.createElement('div');
  grid_head.style.background = 'lightblue';

  if (grid.header_row.length) {  // set up header row if applicable
    var header_row = document.createElement('div');
    header_row.nb_page = null;
    };

  if (grid.footer_row.length) {  // set up footer row if applicable
    var footer_row = document.createElement('div');
    footer_row.nb_page = null;
    };

  grid.appendChild(grid_head);
  for (var i=0, num_cols=grid.num_cols; i<num_cols; i++) {
    var col_defn = col_defns[i];

    if (col_defn[0] === 'input')
      col_defn = col_defn[1];
    else if (col_defn[0] === 'button') {
      col_defn = col_defn[1];
      col_defn.head = col_defn.label;
      var input = {};
      input.can_handle_enter = true;
      input.edit_cell = function(cell) {
        cell.button.afterclick(cell);
        };
      var btn_lng = 0;
      };

    if (i === grid.expand_col)
      col_defn.lng += 17;  // add space for scrollbar

    switch (col_defn.type) {
      case 'text':
        var input = create_cell_input(grid);
        input.aib_obj = new AibText();
        if (col_defn.maxlen)  // 0 means unlimited
          input.maxLength = col_defn.maxlen;
        input.password = col_defn.password;
        if (input.password !== '')
          input.type = 'password';
        //input.style.width = col_defn.lng + 'px';
        input.choices = (col_defn.choices !== null);
        if (input.choices) {
          debug3('DO WE GET HERE?');
          input.choice_data = [];
          input.choice_values = [];
          var choices = col_defn.choices[1];
//          for (var j=0; j<choices.length; j++) {
//            input.choice_data.push(choices[j][0]);
//            input.choice_values.push(choices[j][1]);
          for (var key in choices) {
            var value = choices[key];
            if (typeof(key) === 'number')
              debug3('got number');
            if (typeof(key) === 'number')
              key += '';
            input.choice_data.push(key);
            input.choice_values.push(value)
            };
          };

        var btn_lng = 0;

        if (col_defn.lkup) {
          input.expander = function() {  // press Space or click ButtonTop
            var grid = this.grid;
            if (!grid.amended()) {
              var args = [grid.ref, grid.active_row];
              send_request('start_row', args);
// not sure about this
//              grid.set_amended(true);
              };
            var value = this.grid.active_cell.text_node.data;
            if (value === '\xa0')
              value = ''
            var args = [this.ref, value];
            send_request('req_lookup', args);
            };
          input.lookdown = function() {  // press Shift+Enter or click ButtonBottom
            var grid = this.grid;
            if (!grid.amended()) {
              var args = [grid.ref, grid.active_row];
              send_request('start_row', args);
// not sure about this
//              grid.set_amended(true);
              };
            var args = [this.ref];
            send_request('req_lookdown', args);
            };
//          var btn_lng = 18;
          var btn_lng = 19;  // changed 2017-07-02 - MS Edge problem
          };

        break;
      case 'num':
        var input = create_cell_input(grid);
        input.aib_obj = new AibNum();
        input.integer = col_defn.integer;
        input.neg_display = col_defn.neg_display;
        input.style.textAlign = 'right';
        //input.style.width = col_defn.lng + 'px';
        var btn_lng = 0;
        break;
      case 'date':
        var input = create_cell_input(grid);
        input.aib_obj = new AibDate();
        input.selected = false;
        input.blank = '';
        input.yr_pos = [];
        input.mth_pos = [];
        input.day_pos = [];
        input.literal_pos = [];
        input.input_format = col_defn.input_format;
        input.display_format = col_defn.display_format;
        for (var j=0, l=input.input_format.length; j<l; j++) {
          if (input.input_format[j] === '%') {
            switch(input.input_format[j+1]) {
              case 'd':
                input.day_pos.push(j);
                input.day_pos.push(2);
                input.blank += '  ';
                j += 1;
                break;
              case 'm':
                input.mth_pos.push(j);
                input.mth_pos.push(2);
                input.blank += '  ';
                j += 1;
                break;
              case 'y':
                input.yr_pos.push(j);
                input.yr_pos.push(2);
                input.blank += '  ';
                j += 1;
                break;
              case 'Y':
                input.yr_pos.push(j);
                input.yr_pos.push(4);
                input.blank += '    ';
                j += 1;
                break;
              };
            }
          else {
            input.blank += input.input_format[j];
            input.literal_pos.push(j);
            };
          };

        //input.expander = input.aib_obj.grid_show_cal;
        input.expander = function() {
          this.aib_obj.grid_show_cal(this);
          };
        //input.style.width = col_defn.lng + 'px';
        if (col_defn.readonly === true || grid.readonly === true)
          var btn_lng = 0;
        else
//          var btn_lng = 18;
          var btn_lng = 19;  // changed 2017-07-02 - MS Edge problem
        break;
      case 'bool':
        var input = {};
        input.aib_obj = new AibBool();
        input.images = [iChkBoxUnchk_src, iChkBoxChk_src];
        input.edit_cell = function(cell, current_value, key) {
          if (key === ' ')
            cell.aib_obj.grid_chkbox_change(cell, grid.active_row);
          };
        input.set_value_from_server = function(args) {
          if (this.grid.active_row === -1)  // grid not yet set up
            return
          //var row = this.grid.active_row;
          var row = args[0], value = args[1];
          //var cell = this.grid.grid_rows[row-this.grid.first_grid_row].grid_cols[this.col];
          //cell.aib_obj.set_cell_value_from_server(cell, value);
          this.aib_obj.set_cell_value_from_server(this.grid, row, this.col, value);
// not sure about this
//          this.grid.set_amended(true);
          };
        input.reset_value = function() {
          if (this.grid.active_row === -1)  // grid not yet set up
            return
          var grid = this.grid;
          var cell = grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[this.col];
          this.aib_obj.reset_cell_value(cell);
          };
        input.handle_backslash = function() {
          if (grid.active_row > 0) {
            var value = grid.subset_data[
              grid.first_subset_row + grid.active_row][grid.active_col];
            if (value === '')  // new row
              value = '0';
            var prev_value = grid.subset_data[
              grid.first_subset_row + grid.active_row - 1][grid.active_col];
            if (value !== prev_value) {
              var cell = grid.active_cell;
              cell.aib_obj.grid_chkbox_change(cell, grid.active_row);
              };
            };
          };
        var btn_lng = 0;
        break;
      case 'sxml':
        var input = {};  //new Object();  //document.createElement('span');
//        input.grid = grid;
        input.aib_obj = new AibSxml();
        input.can_handle_enter = true;
        input.edit_cell = function(cell) {
          cell.aib_obj.grid_popup(cell, input, grid.active_row);
          };
//        input.set_readonly = function(state) {
//          input.readonly = state;
//          input.aib_obj.set_readonly(input, state);
//          };
        input.set_value_from_server = function(args) {
          if (this.grid.active_row === -1)  // grid not yet set up
            return
          var row = args[0], value = args[1];
          this.aib_obj.set_cell_value_from_server(this.grid, row, this.col, value);
// not sure about this
//          this.grid.set_amended(true);
          };
        input.reset_value = function() {
          if (this.grid.active_row === -1)  // grid not yet set up
            return
          var grid = this.grid;
          var cell = grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[this.col];
          this.aib_obj.reset_cell_value(cell);
          };
        input.handle_backslash = function() {
          if (grid.active_row > 0) {
            var value = grid.subset_data[
              grid.first_subset_row + grid.active_row][grid.active_col];
            var prev_value = grid.subset_data[
              grid.first_subset_row + grid.active_row - 1][grid.active_col];
            if (value !== prev_value) {
              var cell = grid.active_cell;
              cell.aib_obj.grid_chkbox_change(cell, grid.active_row);
              };
            };
          };
        var btn_lng = 0;
        break;
      case 'choice':
        //var input = {};  //new Object();  //document.createElement('span');
        var input = document.createElement('span');
//        input.grid = grid;
        input.aib_obj = new AibChoice();

        input.data = [];
        input.values = [];
        var choices = col_defn.choices[1];
//        for (var j=0, l=col_defn.choices.length; j<l; j++) {
//          input.data.push(col_defn.choices[j][0]);
//          input.values.push(col_defn.choices[j][1]);
        for (var key in choices) {
          var value = choices[key];
          if (typeof(key) === 'number')
            debug3('got number');
          if (typeof(key) === 'number')
            key += '';
          input.data.push(key);
          input.values.push(value)
          }
        input.dropdown = null;

        input.edit_cell = function(cell, current_value, key) {
          if (key === ' ')
            cell.aib_obj.grid_create_dropdown(cell);
          };

        input.set_value_from_server = function(args) {
          if (this.grid.active_row === -1)  // grid not yet set up
            return
          //var row = this.grid.active_row;
          var row = args[0], value = args[1];
          //var cell = this.grid.grid_rows[row-this.grid.first_grid_row].grid_cols[this.col];
          //cell.aib_obj.set_cell_value_from_server(cell, value);
          this.aib_obj.set_cell_value_from_server(this.grid, row, this.col, value);
// not sure about this
//          this.grid.set_amended(true);
          };

          if (col_defn.readonly === true || grid.readonly === true)
          var btn_lng = 0;
        else
//          var btn_lng = 18;
          var btn_lng = 19;  // changed 2017-07-02 - MS Edge problem
        break;
      };

    input.grid = grid;
    input.ref = col_defn.ref;
    input.col = i;
    input.help_msg = col_defn.help_msg;
    input.readonly = col_defn.readonly;  // set in form defn
    input.allow_amend = col_defn.allow_amend;  // set in col defn
    input.amend_ok = col_defn.amend_ok;  // db permissions
    input.skip = col_defn.skip;
    input.lng = col_defn.lng;

    input.set_readonly = function(state) {
      this.readonly = state;
      //input.aib_obj.set_readonly(input, state);
      };

    input.amendable = function() {
      //if (!cell.input.readonly && (cell.input.allow_amend || grid.inserted)) {
      if (this.readonly) return false;
      if (!this.amend_ok) return false;
      if (this.grid.readonly) return false;
      if (!this.allow_amend && !this.grid.inserted) return false;
      if (!this.allow_amend && !this.grid.growable) return false;
      return true;
      };

    grid.obj_list.push(input);
    frame.form.obj_dict[input.ref] = input;

    var col_span = document.createElement('span');
    col_span.style.display = 'inline-block';
    col_span.style.borderTop = '1px solid black';
    col_span.style.borderBottom = '1px solid black';
    col_span.style.borderRight = '1px solid black';
    if (i === 0)
      col_span.style.borderLeft = '1px solid black';
    col_span.style.width = (+col_defn.lng + btn_lng + 2) + 'px';  // +2 for border
//    grid.grid_width += col_defn.lng + btn_lng + 4;
//    if (i < (col_defns.length - 1))
//      grid.grid_width += 1;
    col_span.style.height = '18px';
    col_span.style.textAlign = 'center';
    col_span.style.fontWeight = 'bold';
    if (col_defn.head === '')
      col_defn.head = '\xa0';
    col_span.appendChild(document.createTextNode(col_defn.head));
    col_span.title = col_defn.help_msg;
    grid_head.appendChild(col_span);

    if (grid.header_row.length) {
      if (grid.header_row[i] === null) {
        var hdr_col = document.createElement('span');
        hdr_col.style.display = 'inline-block';
        hdr_col.style.padding = '1px';
        hdr_col.style[cssFloat] = 'left';
        }
      else if (grid.header_row[i][0] === 'text') {
        var hdr_col = document.createElement('span');
        hdr_col.appendChild(document.createTextNode(grid.header_row[i][1].value));
        hdr_col.style.display = 'inline-block';
        hdr_col.style.padding = '1px';
        hdr_col.style[cssFloat] = 'left';
        }
      else {
        var hdr_col_defn = grid.header_row[i][1]
        var hdr_col = create_input(frame, header_row, hdr_col_defn, null);
        if (hdr_col_defn.type === 'date')
          hdr_col = hdr_col.firstChild;
        };
      header_row.appendChild(hdr_col);
      hdr_col.tabIndex = -1;  // remove from tab order
      hdr_col.style.border = 'none'
      hdr_col.style.borderBottom = '1px solid darkgrey';
      hdr_col.style.borderRight = '1px solid darkgrey';
      if (i === 0)
        hdr_col.style.borderLeft = '1px solid darkgrey';
      hdr_col.style.width = (col_defn.lng + btn_lng) + 'px';
      hdr_col.style.height = '17px';
      hdr_col.style.background = 'rgb(235, 235, 235)';
      };

    if (grid.footer_row.length) {
      if (grid.footer_row[i] === null) {
        var ftr_col = document.createElement('span');
        ftr_col.style.display = 'inline-block';
        ftr_col.style.padding = '1px';
        ftr_col.style[cssFloat] = 'left';
        }
      else if (grid.footer_row[i][0] === 'text') {
        var ftr_col = document.createElement('span');
        ftr_col.appendChild(document.createTextNode(grid.footer_row[i][1].value));
        ftr_col.style.display = 'inline-block';
        ftr_col.style.padding = '1px';
        ftr_col.style[cssFloat] = 'left';
        }
      else {
        var ftr_col_defn = grid.footer_row[i][1]
        var ftr_col = create_input(frame, footer_row, ftr_col_defn, null);
        if (ftr_col_defn.type === 'date')
          ftr_col = ftr_col.firstChild;
        };
      footer_row.appendChild(ftr_col);
      ftr_col.tabIndex = -1;  // remove from tab order
      ftr_col.style.border = 'none'
      ftr_col.style.borderBottom = '1px solid darkgrey';
      ftr_col.style.borderRight = '1px solid darkgrey';
      if (i === 0)
        ftr_col.style.borderLeft = '1px solid darkgrey';
      ftr_col.style.width = (col_defn.lng + btn_lng) + 'px';
      ftr_col.style.height = '17px';
      ftr_col.style.background = 'rgb(235, 235, 235)';
      };

    };

    grid.grid_height += 19;  // col_span height (18) + col_span border (1)
//  main_grid.style.width = grid.offsetWidth + 'px';

  if (grid.header_row.length) {
    grid.appendChild(header_row);
    header_row.style.height = '20px';
    grid.grid_height += 20;
    };

// set up data rows
  grid.grid_rows = [];
  for (var i=0, l=grid.num_grid_rows; i<l; i++) {
//    var grid_row_onoff = document.createElement('div');
//    grid.appendChild(grid_row_onoff);
    var blank_row = document.createElement('div');
    grid.appendChild(blank_row);
    //blank_row.style.width = grid.grid_width + 'px';
    //blank_row.style.height = '21px';
    //blank_row.style.verticalAlign = 'bottom';
    blank_row.style.borderLeft = '1px solid darkgrey';
    blank_row.style.borderRight = '1px solid darkgrey';
    if (i === (grid.num_grid_rows - 1)) {
      blank_row.style.borderBottom = '1px solid darkgrey';
      blank_row.style.height = '19px';
      }
    else
      blank_row.style.height = '20px';

    var grid_row = document.createElement('div');
    grid.appendChild(grid_row);
    grid_row.style.height = '20px';
    //if ((grid.childNodes.length-3) % 4)
    //  grid_row.style.background = 'lightgrey'
    //else
    //  grid_row.style.background = 'white'
    //if (i%2)
    //  grid_row.style.background = '#dddddd';
    //grid_row.style.background = grid_row.background;
    //grid_row.style.border = '1px solid ' + grid_row.background;
    grid.grid_height += 20;
    grid_row.style.display = 'none';
    grid.grid_rows.push(grid_row);
    grid_row.grid_cols = [];

    var data_col = 0;  // to link cell to data column

    // set up data columns
    for (var j=0; j<grid.num_cols; j++) {

      //var col_span = document.createElement('span');
      //col_span.style.display = 'inline-block';
      var col_span = document.createElement('div');
      col_span.style[cssFloat] = 'left';
      grid_row.appendChild(col_span);
      //col_span.style.background = grid_row.background;
      //if ((grid.childNodes.length-3) % 4)
      //  col_span.style.background = 'lightgrey';
      //else
      //  col_span.style.background = 'white';
      //if (i < (grid.num_grid_rows - 1))
      //  col_span.style.borderBottom = '1px solid grey';
      //if (j < (col_defns.length - 1))
      //  col_span.style.borderRight = '1px solid grey';
      //col_span.style.height = '21px';
      col_span.style.borderBottom = '1px solid darkgrey';
      col_span.style.borderRight = '1px solid darkgrey';
      if (j === 0)
        col_span.style.borderLeft = '1px solid darkgrey';

      // set up data cell
      var col_defn = col_defns[j];
      var first = (j === 0), last = (j === (col_defns.length - 1));
      var cell = create_grid_cell(col_span, col_defn, first, last)

      if (col_defn[0] === 'input') {
        cell.data_col = data_col;
        data_col += 1;
        }
      else if (col_defn[0] === 'button')
        cell.data_col = null;

      cell.grid_row = i;
      cell.grid_col = j;
      cell.grid = grid;
      var input = grid.obj_list[j];
      cell.input = input;
      cell.aib_obj = input.aib_obj;

      // prevent selection of text - IE + Chrome + Safari
      cell.onselectstart = function(){return false};
      cell.style.MozUserSelect = 'none';  // prevent selection of text - FF
      cell.unselectable = 'on';  // prevent selection of text - Opera

      cell.onclick = function(e) {

        if (this.style.textDecoration === 'underline') {
          if (grid.frame.form.disable_count) return false;
          var args = [this.input.ref, (this.grid_row + grid.first_grid_row)];
          send_request('clicked', args);
          if (this.grid_row !== grid.active_row || this.grid_col !== grid.active_col)
            grid.req_cell_focus((grid.first_grid_row + this.grid_row), this.grid_col);
          return;
          };
        //debug3('click ' + grid.ref + ' ' + (grid.first_grid_row + this.grid_row)
        //  + '/' + this.grid_col);

        if (grid.frame.form.disable_count) return;

        // with Chrome, grid gets focus first, which should be ok
        // with IE8, sequence is -
        //    onclick
        //    req_cell_focus
        //    grid.onfocus
        // which is not ok
        if (!grid.has_focus) {  // IE8 workaround
          got_focus(grid);
          grid.focus();  //don't know why this is necessary!
          };

        if (grid.edit_in_progress) {
          var input = grid.obj_list[grid.active_col];
            input.end_edit(true, true);
          };

        if (this.grid_row === grid.active_row)
          if (this.grid_col === grid.active_col)
            return;

        grid.req_cell_focus((grid.first_grid_row + this.grid_row), this.grid_col);
        };

      cell.ondblclick = function(e) {
        if (grid.frame.form.disable_count) return;
        callbacks.push([cell, cell.after_dblclick]);

        if (!grid.has_focus) {  // IE8 workaround
          got_focus(grid);
          grid.focus();
          };

        if (grid.edit_in_progress) {
          var input = grid.obj_list[grid.active_col];
            input.end_edit(true, true);
          };

        grid.req_cell_focus((grid.first_grid_row + this.grid_row), this.grid_col);
        };

      cell.after_dblclick = function() {
        if (grid.active_cell !== this)
          return;  // server set focus elsewhere
        grid.edit_cell(null);
        };

      grid_row.grid_cols.push(cell);

      };  // data column set up
    };  // data row set up

  if (grid.footer_row.length) {
    grid.appendChild(footer_row);
    footer_row.style.height = '20px';
    grid.grid_height += 20;
    };

  grid.add_gridframe_indicator = function() {
    var col_span = document.createElement('span');
    col_span.style.display = 'inline-block';
    col_span.style.borderTop = '1px solid black';
    col_span.style.borderBottom = '1px solid black';
    col_span.style.borderRight = '1px solid black';
    col_span.style.width = '20px';
    col_span.style.height = '18px';
    col_span.style.textAlign = 'center';
    col_span.style.fontWeight = 'bold';
    col_span.appendChild(document.createTextNode('\xa0'));
    col_span.title = 'Grid frame indicator';
    grid_head.appendChild(col_span);

    for (var i=0, l=grid.num_grid_rows; i<l; i++) {
      var grid_row = grid.grid_rows[i];
      var col_span = document.createElement('span');
      grid_row.appendChild(col_span);
      col_span.style.marginLeft = '1px';  // don't know why, but it makes it line up nicely!
      col_span.style.width = '20px';
      col_span.style.height = '19px';
      col_span.style[cssFloat] = 'left';
      col_span.style.borderBottom = '1px solid darkgrey';
      col_span.style.borderRight = '1px solid darkgrey';
      col_span.style.textAlign = 'center';
      col_span.style.fontWeight = 'bold';
      col_span.grid_row = i;

      col_span.onclick = function(e) {
        if (grid.frame.form.disable_count) return;
        if (!grid.has_focus) {
          got_focus(grid);
          grid.focus();
          };
        if (grid.edit_in_progress) {
          var input = grid.obj_list[grid.active_col];
            input.end_edit(true, true);
          };
        grid.req_cell_focus((grid.first_grid_row + this.grid_row), 0);
        };
      };

    if (grid.header_row.length) {
      var header_row = grid.childNodes[1];  // to be tested
      var col_span = document.createElement('span');
      header_row.appendChild(col_span);
      col_span.style.marginLeft = '1px';  // don't know why, but it makes it line up nicely!
      col_span.style.width = '20px';
      col_span.style.height = '19px';
      col_span.style[cssFloat] = 'left';
      col_span.style.borderBottom = '1px solid darkgrey';
      col_span.style.borderRight = '1px solid darkgrey';
      col_span.style.background = 'rgb(235, 235, 235)';
      };

    if (grid.footer_row.length) {
      var footer_row = grid.lastChild;
      var col_span = document.createElement('span');
      footer_row.appendChild(col_span);
      col_span.style.marginLeft = '1px';  // don't know why, but it makes it line up nicely!
      col_span.style.width = '20px';
      col_span.style.height = '19px';
      col_span.style[cssFloat] = 'left';
      col_span.style.borderBottom = '1px solid darkgrey';
      col_span.style.borderRight = '1px solid darkgrey';
      col_span.style.background = 'rgb(235, 235, 235)';
      };
    };

//  grid.adjust_size = function() {
//    var table = main_grid.parentNode.parentNode.parentNode.parentNode;
//    if (table.offsetWidth)
//      var table_width = table.offsetWidth
//    else
//      var table_width = parseInt(table.style.width);
//    var req_size = table_width - 22;  // subtract table spacing + cell border
//    var diff = req_size - grid.offsetWidth;
//    if (diff)
//      grid.change_size(diff);
//    };

  // grid.subset_data is values received from server
  // cell.current_value is value entered by user, awaiting validation
  // input.value is value currently being entered by user [DOM element]
  // data_changed - there are 3 scenarios
  // 1 - press Esc while typing
  //   reset value and current_value from form_value
  // 2 - tab off field, fails validation, field gets focus again
  //   Esc - reset value and current_value from form_value
  // 3 - on lost focus, detect whether to send value to server
  //   if yes, get value from input.current_value
  // data_changed compares value with form_value
  // on lost focus, set current_value to value
  // in after_lost_focus, reset value to display format (date/num)

  ////////////////////////
  // events sent to server
  ////////////////////////

  grid.onmousedown = function() {
    if (!grid.has_focus)
      grid.clicked = true;
    };

  grid.onfocus = function() {
    //debug3('grid ' + this.ref + ' got focus');
    if (
        grid.active_row === -1 &&
        grid.active_col === -1 &&
        (grid.frame.form.current_focus === grid)
        )
      // grid has regained focus after start_grid - must execute grid.got_focus()
      grid.frame.form.current_focus = null;
    got_focus(grid);
//    if (grid.highlighted_cell !== null) {
//      var cell = grid.highlighted_cell;
////      if (!cell.input.readonly && (cell.input.allow_amend || grid.inserted)) {
//      if (cell.input.amendable()) {
//        if (grid.err_flag)
//          grid.highlighted_cell.className = 'error_background';
//        else
//          grid.highlighted_cell.className = 'focus_background';
//        };
//      grid.frame.form.help_msg.data = grid.obj_list[grid.active_col].help_msg;
//      };
    };
  grid.got_focus = function() {
    //debug3('grid got focus ' + grid.ref + ' rows=' + grid.num_data_rows
    //  + ' gframe=' + (grid.grid_frame !== null)
    //  + ' from_srv=' + grid.focus_from_server
    //  + ' ins=' + grid.inserted
    //  + ' amd=' + grid.amended()
    //  + ' frame_amd=' + grid.frame.amended());
    //  + ' highlighted=' + ((grid.highlighted_cell === null) ? 'none' :
    //    (grid.highlighted_cell.grid_row + '/' + grid.highlighted_cell.grid_col)));
    //DOMViewerObj = grid;
    //DOMViewerName = null;
    //window.open('../tests/domviewer.html');

    //if (!grid.growable && !grid.num_data_rows)
    //  grid.tab_to_ctrl(grid.frame.form.tabdir);

    if (grid.frame.amended() && !grid.focus_from_server && !grid.frame.form.focus_from_server) {
      var args = [grid.ref];
      send_request('got_focus', args);
      }
    else {
      if (callbacks.length)
        exec_callbacks();
      };

//      if (grid.highlighted_cell === null)
//        grid.cell_set_focus(grid.first_subset_row, 0);
//      else
//        grid.frame.form.help_msg.data = grid.obj_list[grid.active_col].help_msg;

    var set_focus_on_grid_frame = false;
    if (grid.readonly && grid.grid_frame !== null) {
      set_focus_on_grid_frame = true;  // provisional
      if (grid.clicked)  // user clicked on grid
        set_focus_on_grid_frame = false;  // over-ride
      else if (!grid.focus_from_server) {
        var current_focus = grid.frame.form.current_focus;
        if (current_focus !== null)
          if (current_focus.active_frame === grid.active_frame)  // user pressed shift_tab
            set_focus_on_grid_frame = false;  // over-ride
        };
      };

    if (set_focus_on_grid_frame) {
      var grid_frame = grid.grid_frame;
      // find first object to set focus on
      for (var j=0, l=grid_frame.obj_list.length; j<l; j++) {
        var obj = grid_frame.obj_list[j];
        if (!obj.display && obj.offsetHeight)
          break;  // set focus on this obj
        };
      grid_frame.form.focus_from_server = false;
      setTimeout(function() {obj.focus()}, 0);
      };

    grid.clicked = false;
    grid.has_focus = true;
    grid.frame.form.current_focus = grid;

    if (grid.active_row !== -1) {  // else empty grid waiting for cell_set_focus
      grid.highlight_active_cell()
      grid.frame.form.help_msg.data = grid.obj_list[grid.active_col].help_msg;
      }
    else {
      //grid.start_in_progress = true;  // tell set_cell_focus not to set focus on grid
      // when cell gets focus, treat the same as if we had tabbed there
      grid.tabbing = true;
      grid.req_cell_focus(grid.focus_row, 0);
      //grid.start_in_progress = false;
      };

    };

  grid.lost_focus = function() {
    //debug3('grid lost focus ' + grid.ref + ' ' + grid.num_grid_rows +
    //  ' row_amd=' + grid.amended() + ' frame_amd=' + grid.frame.amended());

      if (grid.edit_in_progress) {
        var input = grid.obj_list[grid.active_col];
        input.end_edit(true, false);
        };

    var cell = grid.active_cell;
    cell.highlight('blur');

    if (cell.data_col !== null)
      cell.aib_obj.set_cell_value_lost_focus(cell, cell.current_value);
      if (grid.amended()) {
        var value_for_server =
          cell.aib_obj.get_cell_value_for_server(cell);
        var args =
          [grid.obj_list[grid.active_col].ref, grid.active_row, value_for_server];
        send_request('cell_lost_focus', args);
        if (grid.req_save_row) {
          var args = [grid.ref];
          send_request('req_save_row', args);
          grid.req_save_row = false;
          };
        };

//    if (grid.amended())  // not sure about this - if we find the reason, document it
//      grid.frame.set_amended(true);
    if (grid.frame.amended() && !grid.frame.form.focus_from_server) {
      var value = null;
      var args = [grid.ref, value];
      send_request('lost_focus', args);
      };
    grid.has_focus = false;
    return true;
    };

  grid.req_cell_focus = function(new_row, new_col) {
    //debug3('REQ ' + new_row + '/' + new_col + ' ref=' + grid.ref + ' amended=' + grid.amended()
    //  + ' data_rows=' + grid.num_data_rows + ' active=' + grid.active_row
    //  + ' save=' + grid.req_save_row + ' tabbing=' + grid.tabbing);

//     if (grid.growable)
//       // it will be = if we are on bottom row
//       // it will be > if we are tabbing off bottom row - create new bottom row
//       if (new_row === grid.num_data_rows)  // if new row is bottom row
//         if (new_row === grid.active_row)  // if already on bottom row
// //          grid.set_amended(true);  // force sending 'cell_lost_focus'
//           ;
//         else  // if moving to bottom row
//           new_col = 0;  // move to first column

    if (new_row === grid.num_data_rows)  // new row is bottom row
      if (new_row !== grid.active_row)  // not currently on bottom row
        new_col = 0;  // move to first column

    grid.focus_from_server = false;  // pre-set
    // next line is ugly! [2017-11-08]
    // if active_row is -1, grid has not started, so amended should never be true
    // but we use a trick in setup_periods -
    //    in form.restart_frame > grid.start_row > finperiod_funcs.on_start_row,
    //      we set up values for the first 2 columns, then call grid.redisplay(false)
    //      to indicate that grid has been amended
    // this is necessary to force handle_tab to move to next column, and not exit the grid
    if (grid.active_row !== -1 && grid.amended()) {
      var cell = grid.active_cell;
      if (cell.data_col !== null) {
        var value_for_server =
          cell.aib_obj.get_cell_value_for_server(cell);
        var args =
          [grid.obj_list[grid.active_col].ref, grid.active_row, value_for_server];
        send_request('cell_lost_focus', args);
        };
      var args = [grid.obj_list[new_col].ref, new_row, grid.req_save_row];
      send_request('cell_req_focus', args);
      grid.req_save_row = false;
      return;
      };

    grid.cell_set_focus(new_row, new_col);
    };

  grid.request_rows = function(first_row) {
    if (first_row < 0)
      first_row = 0;
    last_row = first_row + 50;
    if (last_row > this.num_data_rows)
      last_row = this.num_data_rows;
    var args = [this.ref, first_row, last_row];
    send_request('req_rows', args);
    };

  ///////////////////////////////
  // actions received from server
  ///////////////////////////////

  grid.start_grid = function(args) {
    grid.num_data_rows = args[0];
    grid.first_subset_row = args[1];
    grid.subset_data = args[2];
    // if (grid.first_subset_row === 0)
    //   grid.first_grid_row = 0;
    // else
    //   grid.first_grid_row = grid.first_subset_row+1;  // keep 1st row for prev_data

    if (args[3])  // append_row === true
      grid.append_row();

    grid.focus_row = args[4];

    grid.first_grid_row = grid.focus_row - Math.floor(grid.num_grid_rows / 2);
    if (grid.first_grid_row + grid.num_grid_rows > grid.num_data_rows)
        grid.first_grid_row = grid.num_data_rows - grid.num_grid_rows;
    if (grid.first_grid_row < 0)
        grid.first_grid_row = 0;

    var set_focus = args[5];

    if (grid.num_data_rows >= grid.num_grid_rows)
      grid.show_scrollbar();
    else
      grid.hide_scrollbar();

    grid.draw_grid();

    if (grid.row_count !== null)
      grid.row_count.innerHTML = (grid.num_data_rows ? 1 : 0) + '/' + grid.num_data_rows;
/*
    if (!grid.num_data_rows && args[3]) {
      // always req focus when starting a new blank row
      //   to give a chance for a dflt_val to be returned
      var args = [grid.obj_list[0].ref, focus_row, false];
      send_request('cell_req_focus', args);
      grid.inserted = -1;
      }
    else {
      // don't do this above
      // reason - server will send 'cell_set_focus'
      // if row/col = active_row/col, it returns early
      // if there is a dflt_val, it does not get set
      grid.active_row = focus_row;
      grid.active_col = 0;
      grid.active_cell = grid.grid_rows[focus_row].grid_cols[0];
      if (grid.highlighted_cell !== null)
        grid.highlighted_cell.highlight('clear');
      var cell = grid.active_cell;
      cell.highlight('blur');
      grid.highlighted_cell = cell;
      grid.inserted = 0;
      };
*/

    //debug3('start grid ' + grid.ref + ' ' + grid.num_grid_rows + ' ' +
    //  grid.num_data_rows + ' ' + grid.has_focus);
    //debug3(JSON.stringify(grid.subset_data));

    if (!grid.num_data_rows && args[3])
      grid.inserted = -1;
    else
      grid.inserted = 0;

    grid.active_row = -1;
    grid.active_col = -1;
    grid.set_amended(false);

//    // when cell gets focus, treat the same as if we had tabbed there
//    grid.tabbing = true;

//    grid.start_in_progress = true;  // tell set_cell_focus not to set focus on grid
//    grid.req_cell_focus(focus_row, 0);
//    grid.start_in_progress = false;

/*
    grid.active_row = -1;
    grid.active_col = -1;
    if (grid.highlighted_cell !== null)
      grid.highlighted_cell.className = null;
    grid.highlighted_cell = null;

    grid.focus_from_server = true;
    grid.err_flag = false;

    var grid_set_focus = false;
    grid.cell_set_focus(focus_row, 0, grid_set_focus);

    if (!grid.has_focus)
      if (grid.highlighted_cell !== null)
        grid.highlighted_cell.className = 'blur_background';
*/

//    grid.start_row(focus_row);
//    grid.active_row = focus_row;
//    grid.active_col = 0;
//    grid.active_cell = grid.grid_rows[focus_row].grid_cols[0];
//    if (grid.highlighted_cell !== null)
//      grid.highlighted_cell.highlight('clear');
//    var cell = grid.active_cell;
//    cell.highlight('blur');
//    grid.highlighted_cell = cell;

    };

  grid.cell_set_focus = function(new_row, new_col, dflt_val) {
    // can be recd from server, or called from start_grid or req_cell_focus or grid.got_focus

    if (dflt_val === undefined)
      dflt_val = null;

    // debug3('SET FOCUS ' + grid.ref + ' ' + grid.active_row + '/' + grid.active_col +
    //   ' -> ' + new_row + '/' + new_col + ' start_in_prog=' + this.start_in_progress +
    //   ' grid_has_focus=' + grid.has_focus + '  dflt_val=' + dflt_val +
    //   ' from_server=' + grid.focus_from_server);

    if (!grid.start_in_progress)
      if (!grid.has_focus)
//        if (!grid.readonly)
          if (grid.offsetHeight || grid.offsetWidth)  // check if visible
            grid.focus();  // IE8 delays setting focus :-(
            //got_focus(grid);

    if (new_row === -1)  // e.g. cancel_end_row
      new_row = grid.active_row;
    if (new_col === -1)
      new_col = grid.active_col;

    if (new_row === grid.active_row && new_col === grid.active_col) {
      // server returned focus to original cell after error
      // or server returned to grid from grid_frame
      var cell = grid.active_cell;
      if (cell.data_col !== null)
        if (cell.input.amendable())
          cell.aib_obj.set_cell_value_got_focus(cell);
      grid.highlight_active_cell();
      return;
      };

    // if old cell is visible, redisplay using 'display' format
    var old_row = grid.active_row, old_col = grid.active_col;
    if ((old_row >= grid.first_grid_row) &&
        (old_row < (grid.first_grid_row + grid.num_grid_rows))) {
      var cell = grid.grid_rows[old_row-grid.first_grid_row].grid_cols[old_col];
      if (cell.data_col !== null)
        cell.aib_obj.set_cell_value_lost_focus(cell, cell.current_value);
      };

    // added 2017-11-06
    if (grid.focus_from_server)  // else already processed in 'req_cell_focus'
      if (new_row === grid.num_data_rows)  // if new row is bottom row
        if (new_row !== grid.active_row)  // not already on bottom row
          new_col = 0;  // move to first column

    //debug3('SET FOCUS ' + grid.ref + ' ' + grid.active_row + '/' + grid.active_col +
    //  ' -> ' + new_row + '/' + new_col + ' ' + grid.first_grid_row + ' ' + grid.num_grid_rows);

    // ensure cell visible
    // if focus set from server, display active row in centre of grid
    // unless there is an active form (grid.form_row_count !== null)
    // in this case, user is 'navigating' - do not want to adjust position
//  if (grid.first_grid_row > new_row) {
    if (new_row < grid.first_grid_row) {
      if (grid.focus_from_server && grid.form_row_count === null) {
        grid.first_grid_row = (new_row - Math.round(grid.num_grid_rows/2));
        if (grid.first_grid_row < 0) grid.first_grid_row = 0;
        var max_first_row = grid.num_data_rows + 1 - grid.num_grid_rows;
        if (max_first_row < 0) max_first_row = 0;
        if (grid.first_grid_row > max_first_row)
          grid.first_grid_row = max_first_row;
        }
      else
        grid.first_grid_row = new_row;
      grid.draw_grid();
      }
//  else if (grid.first_grid_row < (new_row - grid.num_grid_rows + 1)) {
    else if (new_row > (grid.first_grid_row + grid.num_grid_rows - 1)) {
      if (grid.focus_from_server && grid.form_row_count === null) {
        grid.first_grid_row = (new_row - Math.round(grid.num_grid_rows/2));
        if (grid.first_grid_row < 0) grid.first_grid_row = 0;
        var max_first_row = grid.num_data_rows + 1 - grid.num_grid_rows;
        if (max_first_row < 0) max_first_row = 0;
        if (grid.first_grid_row > max_first_row)
          grid.first_grid_row = max_first_row;
        }
      else
        grid.first_grid_row = (new_row - grid.num_grid_rows + 1);
      grid.draw_grid();
      };

    grid.active_row = new_row;
    grid.active_col = new_col;
    grid.active_cell =
      grid.grid_rows[new_row-grid.first_grid_row].grid_cols[new_col];

    if (new_row !== old_row) {
      if (new_row === grid.num_data_rows)
        grid.inserted = -1;
      else
        grid.inserted = 0;
      grid.start_row(new_row);
      };

    if (!grid.start_in_progress)
      grid.highlight_active_cell();
    var cell = grid.active_cell;
    if (cell.data_col !== null)
      if (cell.input.amendable())
        cell.aib_obj.set_cell_value_got_focus(cell);
// next 2 lines should not be necessary (?)
      else
        cell.aib_obj.set_cell_value_lost_focus(cell, cell.current_value);
    grid.focus_from_server = false;
    grid.err_flag = false;

    if (callbacks.length)  // no request sent, so execute any callbacks now
      exec_callbacks();

    if (dflt_val !== null) {
      var input = grid.obj_list[grid.active_col];
      input.set_dflt_val(dflt_val);
      };

    if (grid.tabbing) {
      grid.tabbing = false;
      var input = grid.obj_list[grid.active_col];
      if (input.skip)
        setTimeout(function() {grid.handle_tab(false, false)}, 0);
      };

    };

  grid.set_amended = function(state) {
    //debug3('gset ' + grid.ref + ' ' + state);
    this._amended = state;
    if (state === true) {
      grid.frame.set_amended(true);  // to force sending lost/got focus for other objects in grid.frame
      if (this.grid_frame !== null)
        this.grid_frame.set_amended(true);
      };
    };

  grid.amended = function() {
    return this._amended;
    };

  grid.set_value_from_server = function(args) {
    // notification of record becoming clean/dirty (true/false)
    var clean = args[0], exists = args[1];
    if (clean) {
      this.set_amended(false);
      if (this.grid_frame !== null)
        this.grid_frame.set_amended(false);
      }
    else {
      this.set_amended(true);
      if (this.grid_frame !== null)
        this.grid_frame.set_amended(true);
      };
    };

  grid.recv_rows = function(args) {
    grid.first_subset_row = args[0];
    grid.subset_data = args[1];
    if (args[2])  // append_row === true
      grid.append_row();
    grid.draw_grid();
    };

  grid.move_row = function(old_row, new_row) {
    // move_row is only called if a blank row is populated, then saved
    // if the blank row was inserted first, num_data_rows has already been incremented
    // but if we were on the bottom 'appended' row, we need to append a new blank row
    if (old_row === new_row) {  // we must have just 'saved' the last row!
      grid.num_data_rows += 1;
      grid.append_row();
      if (grid.num_data_rows >= grid.num_grid_rows)
        grid.show_scrollbar();
      }

    else {
      // old_row is in subset_data, by definition
      // if new_row is in subset_data, delete old row, insert into new, from subset_data
      if ( (new_row >= grid.first_subset_row) &&
          (new_row < (grid.first_subset_row+grid.subset_data.length)) ) {
        var row_data = grid.subset_data[old_row];
        grid.subset_data.splice(old_row, 1);
        grid.subset_data.splice(new_row, 0, row_data);
        };
      // if new_row is not visible, set first_grid_row a few rows up
      if ( (new_row < grid.first_grid_row) ||
          (new_row >= (grid.first_grid_row+grid.num_grid_rows)) )
        grid.first_grid_row = (new_row - Math.round(grid.num_grid_rows/2));
      };

    grid.draw_grid();
    grid.inserted = 0;
    grid.start_in_progress = !grid.auto_startrow;  // don't send 'start_row' to server unless auto
    grid.start_row(new_row);
    grid.start_in_progress = false;
//    grid.active_row = new_row;
//    grid.active_col = 0;
//    grid.active_cell =
//      grid.grid_rows[new_row-grid.first_grid_row].grid_cols[0];
//    grid.highlight_active_cell();
    if (!grid.has_focus)
      grid.focus();
    grid.cell_set_focus(new_row, 0);
    };

  grid.append_row = function() {
    var init_row = [];
    for (var i=0; i<grid.num_cols; i++)
// why was this necessary? [2017-11-04]
// if it *is* necessary, we must change 'date.expander' to convert '\xa0' to ''
//    before calling grid_show_cal()
// if it is *not* necessary, drop above conversion from 'lkup.expander'

//    init_row.push('\xa0');
      init_row.push('');
    grid.subset_data.push(init_row);
    };

  grid.insert_row = function(row) {
    var init_row = [];
    for (var i=0; i<grid.num_cols; i++)
      init_row.push('');
    var subset_rowno = row - grid.first_subset_row;
    grid.subset_data.splice(subset_rowno, 0, init_row);
    grid.num_data_rows += 1;

    if (grid.num_data_rows >= grid.num_grid_rows)
      grid.show_scrollbar();

    if (grid.active_col !== 0)
      grid.active_col = 0;

    grid.draw_grid();
    grid.inserted = 1;
    grid.start_in_progress = !grid.auto_startrow;  // don't send 'start_row' to server unless auto
    grid.start_row(row);
    grid.start_in_progress = false;
    grid.set_amended(true);
    grid.highlight_active_cell();
    };

  grid.delete_row = function(row) {
    var subset_rowno = row - grid.first_subset_row;  // assume it must be in subset
    if (row === grid.num_data_rows) {  // we must be on last row - make blank!
      var init_row = [];
      for (var i=0; i<grid.num_cols; i++)
        init_row.push('');
      grid.subset_data[subset_rowno] = init_row;
      grid.inserted = -1;
      }
    else {
      grid.subset_data.splice(subset_rowno, 1);
      grid.num_data_rows -= 1;
      if (row === grid.num_data_rows)
        grid.inserted = -1;
      else
        grid.inserted = 0;
      if (grid.first_grid_row > 0) {
        if ((grid.first_grid_row + grid.num_grid_rows) > (grid.num_data_rows + 1)) {
          grid.first_grid_row -= 1;
          grid.active_row += 1;
          };
        };
      };

    if (grid.num_data_rows < grid.num_grid_rows) {
      if (grid.first_grid_row > 0)
        grid.first_grid_row = 0;
      grid.hide_scrollbar();
     };

    grid.draw_grid();
    grid.start_in_progress = !grid.auto_startrow;  // don't send 'start_row' to server unless auto
    grid.start_row(row);
    grid.start_in_progress = false;
    grid.set_amended(false);
    grid.highlight_active_cell();
    };

  ///////////////////
  // internal methods
  ///////////////////

  grid.show_scrollbar = function() {
    if (!grid.scrollbar_setup) {
      grid.setup_scrollbar();
      grid.scrollbar_setup = true;
      };
    if (grid.scrollbar.style.display === 'none') {
      grid.change_size(-17);
      grid.scrollbar.style.display = 'block';
      };
    };

  grid.hide_scrollbar = function() {
    if (!grid.scrollbar_setup)
      return;
    if (grid.scrollbar.style.display !== 'none') {
      grid.change_size(17);
      grid.scrollbar.style.display = 'none';
      };
    };

  grid.change_size = function(diff) {
    var expand_col = grid.expand_col;
    var adj_head = grid.firstChild.children[expand_col];
    adj_head.style.width = (parseInt(adj_head.style.width) + diff) + 'px';
    // obscure MS Edge bug [2017-06-17]
    // without this, grid.offsetWidth is not recalculated
    // for some reason, merely referencing it forces a recalc!
    grid.offsetWidth;

    if (grid.header_row.length) {
      var adj_header = grid.childNodes[1].childNodes[expand_col];
      adj_header.style.width = (parseInt(adj_header.style.width) + diff) + 'px';
      };

    if (grid.footer_row.length) {
      var adj_footer = grid.lastChild.childNodes[expand_col];
      adj_footer.style.width = (parseInt(adj_footer.style.width) + diff) + 'px';
      };

    var grid_rows = grid.grid_rows;
    var first_cell = grid_rows[0].grid_cols[expand_col];
    first_cell.style.width = (parseInt(first_cell.style.width) + diff) + 'px';
    for (var j=1, l=grid_rows.length; j<l; j++)
      grid_rows[j].grid_cols[expand_col].style.width = first_cell.style.width;
    };

/*
  grid.tab_to_ctrl = function(tabdir) {
    var pos = grid.pos + tabdir;  // tab = 1, shift+tab = -1
    if (pos < 0) {
      if (grid.frame.type === 'grid_frame') {
        var ctrl_grid = grid.frame.ctrl_grid;
        ctrl_grid.focus();
        ctrl_grid.req_cell_focus(ctrl_grid.active_row, ctrl_grid.num_cols-1);
        return;
        }
      else  // wrap to end
        pos = grid.frame.obj_list.length-1
      }
    else if (pos === grid.frame.obj_list.length)
      pos = 0;  // wrap to start
    while (grid.frame.obj_list[pos].offsetHeight === 0)
      pos += tabdir;  // look for next available object
    setTimeout(function() {grid.frame.obj_list[pos].focus()}, 0);
    };
*/

  grid.tab_to_ctrl = function(tabdir) {
    // next 3 lines added 2017-07-07 - ok??
    var cell = grid.active_cell;
    if (cell.data_col !== null)
      cell.aib_obj.set_cell_value_lost_focus(cell, cell.current_value);
    var pos = grid.pos + tabdir;  // tab = 1, shift+tab = -1
    while (true) {
      if (pos < 0) {
        if (grid.frame.type === 'grid_frame') {
          var ctrl_grid = grid.frame.ctrl_grid;
          ctrl_grid.focus();
          ctrl_grid.req_cell_focus(ctrl_grid.active_row, ctrl_grid.num_cols-1);
          break;
          }
        else  // wrap to end
          pos = grid.frame.obj_list.length-1;
        }
      else if (pos === grid.frame.obj_list.length) {
        pos = 0;  // wrap to start
        };
      var next_obj = grid.frame.obj_list[pos];
      if (next_obj.offsetHeight > 0 && !next_obj.display && next_obj.tabIndex > -1) {
        setTimeout(function() {next_obj.focus()}, 0);
        break;
        };
      pos += tabdir;  // tab = 1, shift+tab = -1
      };
    };

  grid.start_row = function(row) {
    //debug3('START ROW ref=' + grid.ref + ' row=' + row +
    //  ' ins=' + grid.inserted + ' gframe=' + (grid.grid_frame !== null));
    if (grid.row_count !== null)
      grid.row_count.innerHTML = (row+1) + '/' + grid.num_data_rows;
    if (grid.form_row_count !== null)
      grid.form_row_count.innerHTML = (row+1) + '/' + grid.num_data_rows;

//    grid.set_amended(false);
//    if (grid.grid_frame !== null)
//      grid.grid_frame.set_amended(false);

    if (grid.grid_frame !== null)
      grid.highlight_active_row();

    if (!grid.start_in_progress && !grid.focus_from_server)
      if (grid.grid_frame !== null || grid.auto_startrow) {
        var args = [grid.ref, row];
        send_request('start_row', args);
        };
    };

  grid.draw_grid = function() {
    // grid.first_grid_row has been pre-calculated as the first row to display
    // STEP 1 - ensure data to display exists in subset_data

    var min = grid.first_subset_row + (grid.first_subset_row > 0);  // keep 1st row for prev_val
    var max = grid.first_subset_row + grid.subset_data.length - grid.num_grid_rows;
    if (max < 0) max = 0;

    if (grid.first_grid_row < min) {  // assume page up - get previous 40 rows
      var first_req_row = grid.first_grid_row - 40 + grid.num_grid_rows;
      if (first_req_row < 0)
        first_req_row = 0;
      grid.request_rows(first_req_row);
      return;  // grid will be drawn when rows received
      }
    else if (grid.first_grid_row > max) {  // assume page down - get next 40 rows
      var first_req_row = grid.first_grid_row - 10;
      if (first_req_row > (grid.num_data_rows - 50))
        first_req_row = grid.num_data_rows - 50;
      grid.request_rows(first_req_row);
      return;  // grid will be drawn when rows received
      };

    // STEP 2 - draw grid data
    var height_diff = grid.clientHeight;  // check again after drawing
    var start_row = grid.first_grid_row;
    var end_row = start_row + grid.num_grid_rows;

    var rows_to_skip = 1 + (grid.header_row.length ? 1 : 0); // 1 for heading, 1 for header_row if exists

    for (var row=start_row; row<end_row; row++) {
      var display_row = row-grid.first_grid_row;
      var blank_row = grid.childNodes[display_row*2 + rows_to_skip];
      var data_row = grid.childNodes[display_row*2 + rows_to_skip + 1];
      if (row > grid.num_data_rows) {
        //row must be blank
        blank_row.style.display = 'block'
        data_row.style.display = 'none'
        }
      else {
        //row must not be blank
        blank_row.style.display = 'none'
        data_row.style.display = 'block'
        var row_data = grid.subset_data[row - grid.first_subset_row];
        if (row_data === undefined)
          debug3('ERR ' + row + ' ' + grid.first_subset_row);
        for (var col=0; col<grid.num_cols; col++) {
          var cell = grid.grid_rows[row-start_row].grid_cols[col];
          if (cell.data_col !== null)
            cell.aib_obj.set_cell_value_lost_focus(cell, row_data[cell.data_col]);
          };
        };
//      show_all = function(elem, level) {
//        debug3(level + ': ' + String(elem) + ' ' + elem.clientHeight + ' ' + elem.offsetHeight);
//        for (var j=0; j<elem.childNodes.length; j++)
//          show_all(elem.childNodes[j], level+1)
//        };
//        if (row === 0)
//          show_all(display_node, 0);
      };

    height_diff -= grid.clientHeight;  // if not 0, height has changed

    // STEP 3 - wrap up
    if (grid.scrollbar_setup) {
      var scrollbar = grid.scrollbar;
      if (scrollbar.style.display !== 'none') {
        if (height_diff) {  // height has changed - adjust scrollbar
          scrollbar.slider.slider_height -= height_diff;
          scrollbar.slider.style.height = scrollbar.slider.slider_height + 'px';
          scrollbar.thumb.maxY = (scrollbar.slider.slider_height-scrollbar.thumb.thumb_height);
          };
        scrollbar.thumb.move_thumb();
        };
      };
    };

  grid.highlight_active_cell = function() {
//    if (grid.grid_frame !== null)
//      return;  // we should not get here, but we do!

    if (grid.highlighted_cell !== null) {
//      grid.highlighted_cell.firstChild.style.background = '#f5f5f5';  // very light grey
//      grid.highlighted_cell.className = null;

      grid.highlighted_cell.highlight('clear');

//    var cell = grid.highlighted_cell;
//    var border = '1px solid darkgrey';
//    var col_span = cell.parentNode;

//    cell.firstChild.style.background = '#f5f5f5';
//    cell.className = 'blur_background';

//    col_span.style.borderBottom = border;
//    col_span.style.borderRight = border;
//    if (cell.grid_row)
//      grid.childNodes[((cell.grid_row-1)*2)+2]
//        .childNodes[cell.grid_col].style.borderBottom = border;
//    if (cell.grid_col)
//      grid.childNodes[(cell.grid_row*2)+2]
//        .childNodes[(cell.grid_col-1)].style.borderRight = border;
//    else
//      col_span.style.borderLeft = border;

      };

    if (grid.active_row < grid.first_grid_row)
      grid.highlighted_cell = null;
    else if (grid.active_row >= (grid.first_grid_row + grid.num_grid_rows))
      grid.highlighted_cell = null;
    else {
      var cell = grid.active_cell;
//      if ((cell.data_col !== null) && (cell.input.readonly ||
//          !(cell.input.allow_amend || grid.inserted)))
      if (!grid.has_focus)
        var state = 'blur'
      else if (cell.data_col !== null && !cell.input.amendable())
        var state = 'readonly'
      else if (grid.err_flag)
        var state = 'error'
      else
        var state = 'focus';
      cell.highlight(state);
      grid.highlighted_cell = cell;

//    var cell = grid.highlighted_cell;
//    var border = '1px solid black';
//    var col_span = cell.parentNode;

////    if (!cell.input.readonly && (cell.input.allow_amend || grid.inserted)) {
//    if (cell.input.amendable()) {
//      if (grid.err_flag)
//        cell.className = 'error_background';
//      else
//        cell.className = 'focus_background';
//      cell.firstChild.style.background = '#c0ffff';
//      };

//    col_span.style.borderBottom = border;
//    col_span.style.borderRight = border;
//    if (cell.grid_row)
//      grid.childNodes[((cell.grid_row-1)*2)+2]
//        .childNodes[cell.grid_col].style.borderBottom = border;
//    if (cell.grid_col)
//      grid.childNodes[(cell.grid_row*2)+2]
//        .childNodes[(cell.grid_col-1)].style.borderRight = border;
//    else
//      col_span.style.borderLeft = border;

      grid.frame.form.help_msg.data = grid.obj_list[grid.active_col].help_msg;
      };
    };

  grid.unhighlight_active_row = function() {
//    if (grid.active_frame !== grid.frame.form.active_frame)
//      return;
    if (grid.highlighted_row !== null) {
      var row = grid.highlighted_row;
      row.lastChild.innerHTML = '\xa0';
      // for (var col=0, no_cols = row.childNodes.length; col<no_cols; col++) {
      //   var cell = row.childNodes[col].firstChild;
      //   cell.set_row_highlight('1px solid darkslategrey');
      //   };
      };
    };

  grid.highlight_active_row = function() {
    if (grid.active_frame === grid.frame.form.active_frame)
      var border = '1px solid blue';
    else
      var border = '1px solid darkslategrey';
    if (grid.highlighted_row !== null) {
      var row = grid.highlighted_row;
      row.lastChild.innerHTML = '\xa0';
      // for (var col=0, no_cols = row.childNodes.length; col<no_cols; col++) {
      //   var cell = row.childNodes[col].firstChild;
      //   cell.set_row_highlight('1px solid transparent');
      //   };
      };
    if (grid.active_row < grid.first_grid_row)
      grid.highlighted_row = null;
    else if (grid.active_row >= (grid.first_grid_row + grid.num_grid_rows))
      grid.highlighted_row = null;
    else {
      var row = grid.grid_rows[grid.active_row-grid.first_grid_row];
      row.lastChild.innerHTML = '\u2190';  // left arrow
      // for (var col=0, no_cols = row.childNodes.length; col<no_cols; col++) {
      //   var cell = row.childNodes[col].firstChild;
      //   cell.set_row_highlight(border);
      //   };
      grid.highlighted_row = row;
      };
    grid.frame.form.help_msg.data = grid.obj_list[0].help_msg;
    };

//  grid.get_active_cell = function() {
//    return grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[grid.active_col];
//    };

// KEY HANDLING FUNCTIONS
  grid.handle_escape = function() {
    // TO BE IMPLEMENTED [2013-08-21]
    // if cell_data_changed, restore cell value
    // if grid_amended and not inserted, ask if ok, then restore row
    // if grid_amended and inserted === 1, ask if ok, then delete row
    // if not grid_amended and inserted === 1, delete row
    // if grid_amended and inserted === -1, ask if ok, then restore blank row
    // else send req_cancel

    //var cell = grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[grid.active_col];
    var cell = grid.active_cell;

    if (cell !== null && cell.data_col !== null && cell.aib_obj.cell_data_changed(cell)
        && cell.input.amendable()) {
      cell.aib_obj.reset_cell_value(cell);
      // the next two lines are a bodge, added on 2017-10-26
      // if grid has one column, you start to add a value, then backspace and press Tab,
      //    an empty string is sent to server, and validation fails
      // you can press Esc to reset the value, but the grid is still in an 'amended'
      //   state, which causes problems
      // this fixes it, but it is not a true fix - what if there are > 1 columns ??
      if (grid.num_cols === 1)
        grid.set_amended(false);
      }
    else {
      var args = [grid.ref];
      send_request('req_cancel', args);
      };

/*
    //debug3('ESC "' + cell.firstChild.data + '" "' + grid.obj_list[grid.active_col].value + '"');

    var value = grid.subset_data[grid.active_row - grid.first_subset_row][grid.active_col];
    var cell = grid.active_cell;
    if (cell.aib_obj.get_cell_value_for_server(cell) === value)
      ; //debug3('ESCAPE');
    else {
      cell.aib_obj.set_cell_value_lost_focus(cell, value);
      cell.aib_obj.set_cell_value_got_focus(cell);
      };

//    if (cell.firstChild.data === grid.obj_list[grid.active_col].value)
//      debug3('ESCAPE');
//    else  // restore unedited value
//      cell.firstChild.data = grid.obj_list[grid.active_col].value;
*/
    };

/*
  grid.req_formview = function() {
    if (grid.formview_ok) {
      var args = [grid.ref, grid.active_row];
      send_request('formview', args);
      //var args = [grid.formview_ok, grid.active_row];
      //send_request('clicked', args);
      };
    };
*/

/*
  grid.send_selected = function() {
    if (grid.lkup_select_ok) {
      var args = [grid.ref, grid.active_row];
      //send_request('start_row', args);
      //var args = [grid.lkup_selected, grid.active_row];
      //send_request('clicked', args);
      send_request('selected', args);
      };
    };
*/

  grid.handle_enter = function() {

    var cell = grid.active_cell;
    var input = grid.obj_list[grid.active_col];
    if (cell.style.textDecoration === 'underline') {
      if (grid.frame.form.disable_count) return false;
      var args = [input.ref, (cell.grid_row + grid.first_grid_row)];
      send_request('clicked', args);
      return;
      };

    if (input.can_handle_enter) {  // i.e. sxml - uses <enter> to open popup
      input.edit_cell(grid.active_cell);
      return;
      };

    if (grid.amended())
      grid.req_save_row = true;
    //debug3('here ' + grid.req_save_row + ' ' + grid.active_row + ' ' + grid.num_data_rows);
    if ((grid.active_row < grid.num_data_rows) || grid.req_save_row) {
      grid.tabbing = true;
      grid.req_cell_focus(grid.active_row+1, grid.active_col);
      }
    else {
      grid.tab_to_ctrl(1);
      };
    };

  grid.edit_cell = function(key) {
    var input = grid.obj_list[grid.active_col];
    if (!input.amendable())
      return;
    input.edit_cell(grid.active_cell, null, key);
    };

  grid.clear_cell = function() {
    var input = grid.obj_list[grid.active_col];
    if (!input.amendable())
      return;
    input.clear_cell(grid.active_cell);
    };

  grid.handle_tab = function(shiftKey) {
    //debug3('TAB ' + document.getElementsByTagName('*').length + ' ' +
    //  document.getElementsByTagName('*')[document.getElementsByTagName('*').length-1]);

/*
    if (grid.grid_frame !== null) {  // special handling for grid_frame
      if (shiftKey)  //move to previous control on form
        grid.tab_to_ctrl(-1);
      else {  // move to grid_frame
        var grid_frame = grid.grid_frame.ref;
        var frame_amended = (grid.inserted !== 0);
        var set_focus = true;
        var args = [grid_frame, frame_amended, set_focus];
        start_frame(args);
        grid.has_focus = false;  // not elegant!
        };
      return;
      };
*/

//    if (grid.grid_frame !== null) {  // special handling for grid_frame
//      if (shiftKey)  //move to previous control on form
//        grid.tab_to_ctrl(-1);
//      else  // move to grid_frame
//        start_frame([grid.grid_frame.ref, grid.amended(), true]);
//        grid.has_focus = false;  // not elegant!
//      return;
//      };
    if (shiftKey) {
      grid.frame.form.tabdir = -1;

      // if not on first cell in row, try move to previous cell
      if (grid.active_col > 0)
        grid.req_cell_focus(grid.active_row, grid.active_col-1);

//      else if (grid.grid_frame !== null)
//        grid.tab_to_ctrl(-1);  //move to previous control on form

      // if not on first row, try move to last cell in previous row
      else if (grid.active_row > 0)
        grid.req_cell_focus(grid.active_row-1, grid.num_cols-1);

      // else move to previous control on form
      else
        grid.tab_to_ctrl(-1);
      }

    else {
      grid.frame.form.tabdir = 1;

      //debug3('TAB ' + grid.ref + ' grow=' + grid.growable + ' num_rows=' + grid.num_data_rows
      //  + ' active=' + grid.active_row + '/' + grid.active_col
      //  + ' amended=' + grid.amended() + ' grid_frame=' + (grid.grid_frame !== null)
      //  + ' readonly=' + grid.readonly + ' inserted=' + grid.inserted);

      // if readonly and grid_frame, move directly to grid_frame
      if (grid.readonly && (grid.grid_frame !== null)) {
        var grid_frame = grid.grid_frame;
        // find first object to set focus on
        for (var j=0, l=grid_frame.obj_list.length; j<l; j++) {
          var obj = grid_frame.obj_list[j];
          if (!obj.display && obj.offsetHeight)
            break;  // set focus on this obj
          };
        grid_frame.form.focus_from_server = false;
        setTimeout(function() {obj.focus()}, 0);
        }

      // if growable and on bottom blank line and tab, move to next control
//      else if (grid.growable && (grid.active_row === grid.num_data_rows) &&
//          (grid.active_col === 0) && (!grid.amended()))
      else if (grid.inserted === -1  && !grid.amended())
        grid.tab_to_ctrl(1)  //  move to next control on form

// move next 4 lines to below grid_frame
//    // if not growable and on last cell and tab, move to next control
//    else if (!grid.growable && (grid.active_row === grid.num_data_rows-1) &&
//        (grid.active_col === grid.num_cols-1))
//      grid.tab_to_ctrl(1)  //  move to next control on form

      // if not on last cell in row, try move to next cell
      else if (grid.active_col < (grid.num_cols-1)) {
        grid.tabbing = true;
        grid.req_cell_focus(grid.active_row, grid.active_col+1);
        }

      // if on last cell and grid_frame, move to grid frame
      else if (grid.grid_frame !== null) {  // move to grid_frame
//      if (grid.amended()) {
//        var cell = grid.active_cell;
//        var value_for_server = cell.aib_obj.get_cell_value_for_server(cell);
//        var args =
//          [grid.obj_list[grid.active_col].ref, grid.active_row, value_for_server];
//        send_request('cell_lost_focus', args);
//        var args = [grid.ref];
//        send_request('gridframe_got_focus', args);
//        };
//      //var grid_frame = grid.grid_frame.ref;
//      //var frame_amended = (grid.amended());
//      //var set_focus = true;
//      //var args = [grid_frame, frame_amended, set_focus];
//      //start_frame(args);
//
//      // args = [grid_frame, frame_amended, set_focus]

//        var grid_frame = grid.grid_frame.ref;
//        var frame_amended = (grid.inserted !== 0 || grid.amended());
//        var set_focus = true;
//        var args = [grid_frame, frame_amended, set_focus];
//        start_frame(args);
//        grid.has_focus = false;  // not elegant!

        var grid_frame = grid.grid_frame;
// should not be necessary - set in got_focus()
//        grid_frame.set_amended(grid.amended());
// should not be necessary - set in start_frame
//        grid_frame.obj_exists = (grid.inserted === 0);

        // find first object to set focus on
        for (var j=0, l=grid_frame.obj_list.length; j<l; j++) {
          var obj = grid_frame.obj_list[j];
//          if (obj.display || !obj.offsetHeight)
//            continue;  // look for the next obj
//          else
//            break;  // set focus on this obj
          if (!obj.display && obj.offsetHeight)
            break;  // set focus on this obj
          };
        grid_frame.form.focus_from_server = false;
        setTimeout(function() {obj.focus()}, 0);

        }

// removed [2017-08-15] - there is always a bottom row, even if not growable
//      // if not growable and on last cell and tab, move to next control
//      else if (!grid.growable && (grid.active_row === grid.num_data_rows-1) &&
//          (grid.active_col === grid.num_cols-1)) {
//        // DO WE EVER GET HERE? - yes, e.g. party_setup > messaging
//        if (grid.amended())
//          grid.req_save_row = true;
//        grid.tab_to_ctrl(1)  //  move to next control on form
//        }

      // on last cell in row - req move to next row, send 'save = true' to server
      else {
        if (grid.amended())
          grid.req_save_row = true;
        grid.tabbing = true;
        grid.req_cell_focus(grid.active_row+1, 0);
        };
      };
    };
  grid.left = function() {
    grid.handle_tab(true);  // treat the same as shift_tab
    };
  grid.right = function() {
    grid.handle_tab(false);  // treat the same as tab
    };
  grid.up = function() {
    if (grid.active_row > 0)
      grid.req_cell_focus(grid.active_row-1, grid.active_col);
    };
  grid.down = function() {
    if (grid.active_row < grid.num_data_rows)
      grid.req_cell_focus(grid.active_row+1, grid.active_col);
    };
/*
  grid.req_insert = function() {
    if (grid.insert_ok) {
      var args = [grid.ref, grid.active_row];
      send_request('req_insert_row', args);
      };
    };
*/
/*
  grid.req_delete = function() {
    if (grid.inserted === -1 && !grid.amended())
      return
    if (grid.delete_ok) {
      if (grid.confirm_delete) {
        if (grid.inserted === 1 && !grid.amended())
          grid.confirm_req('Yes');  // no confirmation required
        else {
          var cell = grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[0];
          args = [null, 'Delete?',
            "Sure you want to delete '" + cell.current_value + "'?",
            ['Yes', 'No'], 'No', 'No', [grid, grid.confirm_req]];
          ask_question(args);
          };
        }
      else
        grid.confirm_req('Yes');
      };
    };
  grid.confirm_req = function(answer) {
    if (answer === 'Yes') {
      var args = [grid.ref, grid.active_row];
      send_request('req_delete_row', args);
      };
    };
*/
  grid.goto_top = function() {
    if (grid.active_row > 0)  // maybe test for active_col > 0 (?)
      grid.req_cell_focus(0, 0);
    };
  grid.goto_bottom = function() {
    if (grid.active_row < grid.num_data_rows)
      grid.req_cell_focus(grid.num_data_rows, 0);
    };
  grid.page_up = function() {
    if (grid.active_row > 0) {
      if (grid.active_row > grid.first_grid_row)
        grid.req_cell_focus(grid.first_grid_row, grid.active_col);
      else {
        var new_row = grid.active_row - grid.num_grid_rows;
        if (new_row < 0)
          new_row = 0;
        grid.req_cell_focus(new_row, grid.active_col);
        };
      };
    };
  grid.page_down = function() {
    if (grid.active_row < grid.num_data_rows) {
      if (grid.active_row < (grid.first_grid_row + grid.num_grid_rows - 1))
        var new_row = grid.first_grid_row + grid.num_grid_rows - 1;
      else
        var new_row = grid.active_row + grid.num_grid_rows;
      if (new_row > grid.num_data_rows)
        new_row = grid.num_data_rows;
      grid.req_cell_focus(new_row, grid.active_col);
      };
    };

  grid.onkeydown = function(e) {
    if (grid.frame.form.disable_count) return false;
    if (e.altKey)
      var target = grid.kbd_shortcuts['alt'][e.code];
    else if (e.ctrlKey)
      var target = grid.kbd_shortcuts['ctrl'][e.code];
    else if (e.shiftKey)
      var target = grid.kbd_shortcuts['shift'][e.code];
    else if (!grid.amended())  // Enter can mean 'save' if amended, or 'select' if not
      var target = grid.kbd_shortcuts['normal'][e.code];

    if (target !== undefined) {
      target.onclick.call(target);
      e.cancelBubble = true;
      return false;
      };

    if (e.altKey)
      return;
    if (e.ctrlKey)
      if (!['Home', 'End', 'Insert', 'Delete'].includes(e.key))
        return;
    var key_handled = true;
    switch (e.key) {
      case 'Tab':  grid.handle_tab(e.shiftKey); break;
      case 'Enter': grid.handle_enter(); break;
      case 'Escape': grid.handle_escape(); break;
      case 'PageUp': grid.page_up(); break;
      case 'PageDown': grid.page_down(); break;
      case 'Home': if (e.ctrlKey) {grid.goto_top()}; break;
      case 'End': if (e.ctrlKey) {grid.goto_bottom()}; break;
      case 'ArrowLeft': grid.left(); break;
      case 'ArrowUp': grid.up(); break;
      case 'ArrowRight': grid.right(); break;
      case 'ArrowDown': grid.down(); break;
      case 'Delete': if (!e.ctrlKey) {grid.clear_cell()}; break;
      case 'F2': grid.edit_cell(null); break;
      default: key_handled = false;
      };
    if (key_handled) {
      // e.cancelBubble = true;
      e.stopPropagation();
      return false;
      };
    var input = grid.obj_list[grid.active_col];
    if (e.key === '\\') {
      input.handle_backslash();
      return false;
      };
    if (e.key === ' ' && (input.expander !== undefined)) {
      input.cell = grid.active_cell;
      input.expander(input);
      return false;
      };
    if (e.key.length === 1 && !e.ctrlKey && !e.altKey) {
      grid.edit_cell(e.key);
      return false;
      };
    };

// SCROLLBAR SETUP AND FUNCTIONS
  grid.setup_scrollbar = function() {

    var scrollbar = document.createElement('div');
    scrollbar.style[cssFloat] = 'left';
    scrollbar.style.display = 'none';
    main_grid.appendChild(scrollbar);
    grid.scrollbar = scrollbar;

    var up = document.createElement('div');
    scrollbar.appendChild(up);
    up.style.width = '13px';
    up.style.height = '13px';
    up.style.margin = '1px';
    up.style.borderTop = '1px solid white';
    up.style.borderLeft = '1px solid white';
    up.style.borderRight = '1px solid black';
    up.style.borderBottom = '1px solid black';
    //up.style.background = 'silver';
    //up.style.position = 'relative';
    up.style.backgroundImage = 'url(' + iScrollUp_src + ')';
    up.onclick = function(e) {
      grid.focus();
      if (grid.frame.form.disable_count) return false;
      if (grid.first_grid_row === 0)
        return;
      grid.first_grid_row -= 1;
      grid.draw_grid();
      grid.highlight_active_cell();
      if (grid.grid_frame !== null)
        grid.highlight_active_row();
      };

    /*
    var canvas = new_canvas(13, 13, up);
    canvas.style.borderTop = '1px solid white';
    canvas.style.borderLeft = '1px solid white';
    canvas.style.borderRight = '1px solid black';
    canvas.style.borderBottom = '1px solid black';

    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(6.5, 4.5);
    ctx.lineTo(2.5, 8.5);
    ctx.lineTo(10.5, 8.5);
    ctx.fillStyle = 'black';
    ctx.fill();
    */

    var slider = document.createElement('div');
    var slider_height = grid.grid_height - 32;
    slider.slider_height = slider_height;
    slider.style.height = slider_height + 'px';
    slider.style.width = '16px';
    slider.style.background = 'whitesmoke';
    slider.style.position = 'relative';
    scrollbar.appendChild(slider);
    scrollbar.slider = slider;
    slider.onclick = function(e) {
      if (!e) e=window.event;
      if (grid.frame.form.disable_count) return false;
      var thumb_top = find_pos(this.thumb)[1];
      if (e.clientY < thumb_top) {  // page up
        if (grid.first_grid_row === 0)
          return;  // should never get here - no space to click!
        grid.first_grid_row -= grid.num_grid_rows;
        if (grid.first_grid_row < 0)
          grid.first_grid_row = 0;
        grid.draw_grid();
        grid.highlight_active_cell();
        if (grid.grid_frame !== null)
          grid.highlight_active_row();
        }
      else if (e.clientY > (thumb_top + this.thumb.offsetHeight)) {  // page down
        var max_first_row = grid.num_data_rows + 1 - grid.num_grid_rows;
        if (grid.first_grid_row === max_first_row)
          return;  // should never get here - no space to click!
        grid.first_grid_row += grid.num_grid_rows;
        if (grid.first_grid_row > max_first_row)
          grid.first_grid_row = max_first_row;
        grid.draw_grid();
        grid.highlight_active_cell();
        if (grid.grid_frame !== null)
          grid.highlight_active_row();
        }
      grid.focus();
      };

    var thumb = document.createElement('div');
    var thumb_height = Math.round(slider_height / (this.num_data_rows+1) * this.num_grid_rows);
    if (thumb_height < 15) thumb_height = 15;  // minimum size
    thumb.style.height = thumb_height + 'px';
    thumb.style.width = '13px';
    thumb.style.marginLeft = '1px';
    thumb.style.background = 'silver';
    thumb.style.borderTop = '1px solid white';
    thumb.style.borderLeft = '1px solid white';
    thumb.style.borderRight = '1px solid black';
    thumb.style.borderBottom = '1px solid black';
    thumb.style.position = 'relative';
    thumb.style.top = '0px';
    thumb_height += 2; // adjust for margins
    thumb.thumb_height = thumb_height;
    //thumb.grid = this;
    Drag.init(thumb, null, 0, 0, 0, (slider_height-thumb_height));
    thumb.onDragStart = function(x, y) {
      if (grid.frame.form.disable_count) return false;
      return true;
      };
    thumb.onDragEnd = function(x, y) {
      grid.first_grid_row = this.get_row(y);
      grid.draw_grid();
      grid.highlight_active_cell();
      if (grid.grid_frame !== null)
        grid.highlight_active_row();
      grid.focus();
      };
    thumb.get_row = function(y) {
      return Math.round(
        ((grid.num_data_rows+1) - grid.num_grid_rows) /
          (slider.slider_height - thumb.thumb_height) * y);
      };
    thumb.move_thumb = function() {
      var max = slider.slider_height - thumb.thumb_height;
      var max_first_row = (grid.num_data_rows+1) - grid.num_grid_rows;
      var new_top = Math.round(grid.first_grid_row / max_first_row * max);
      if (new_top !== parseInt(thumb.style.top))
        thumb.style.top = new_top + 'px';
      };
    //thumb.grid = scrollbar.parentNode.grid;
    slider.appendChild(thumb);
    slider.thumb = thumb;
    scrollbar.thumb = thumb;

    var dn = document.createElement('div');
    scrollbar.appendChild(dn);
    dn.style.width = '13px';
    dn.style.height = '13px';
    dn.style.margin = '1px';
    dn.style.borderTop = '1px solid white';
    dn.style.borderLeft = '1px solid white';
    dn.style.borderRight = '1px solid black';
    dn.style.borderBottom = '1px solid black';
    //dn.style.background = 'silver';
    //dn.style.position = 'relative';
    dn.style.backgroundImage = 'url(' + iScrollDown_src + ')';
    dn.onclick = function(e) {
      grid.focus();
      if (grid.frame.form.disable_count) return false;
      if (grid.first_grid_row === (grid.num_data_rows + 1 - grid.num_grid_rows))
        return;
      grid.first_grid_row += 1;
      grid.draw_grid();
      grid.highlight_active_cell();
      if (grid.grid_frame !== null)
        grid.highlight_active_row();
      };

    /*
    var canvas = new_canvas(13, 13, dn);
    canvas.style.borderTop = '1px solid white';
    canvas.style.borderLeft = '1px solid white';
    canvas.style.borderRight = '1px solid black';
    canvas.style.borderBottom = '1px solid black';

    var ctx = canvas.getContext('2d');
    ctx.beginPath();
    ctx.moveTo(6.5, 8.5);
    ctx.lineTo(2.5, 4.5);
    ctx.lineTo(10.5, 4.5);
    ctx.fillStyle = 'black';
    ctx.fill();
    */

    };

// TOOLBAR SETUP AND FUNCTIONS
  main_grid.create_grid_toolbar = function(json_args) {
    //debug3(JSON.stringify(json_args));

    var toolbar = document.createElement('div');
    this.insertBefore(toolbar, this.firstChild);
    toolbar.style.border = '1px solid lightgrey';
    toolbar.style.height = '28px';
    toolbar.grid = this.grid;
    var title = json_args[0], tool_list = json_args[1];
    if (title !== null) {
      var text = document.createElement('span');
      text.appendChild(document.createTextNode(title));
      text.style.fontWeight = 'bold';
      text.style.marginLeft = '5px';
      text.style.marginTop = '5px';
      text.style.marginRight = '10px';
      text.style[cssFloat] = 'left';
      toolbar.appendChild(text);
      };
    for (var i=0, l=tool_list.length; i<l; i++) {
      tool = tool_list[i];
      switch(tool.type) {
        case 'btn':
          var label = tool.label;
          var text = '';  // convert '&' to underline
          for (var j=0, m=label.length; j<m; j++) {
            if (label[j] === '&') {
              if (label[j+1] === '&')
                text += '&';
              else {
                // set up Alt+label[j+1] as hotkey? No, use 'shortcut' parameter
                text += '<u>';
                text += label[j+1];
                text += '</u>';
                };
              j++;
              }
            else
              text += label[j];
            }
          var btn = document.createElement('div');
          btn.style[cssFloat] = 'left';
          frame.form.obj_dict[tool.ref] = btn;
          btn.tabIndex = -1  // remove from tab order
          btn.ref = tool.ref;
          btn.style.border = '1px solid darkgrey';
          btn.style.marginLeft = '5px';
          btn.style.marginRight = '5px';
          btn.style.marginTop = '4px';
          btn.style.paddingLeft = '5px';
          btn.style.paddingRight = '5px';
          btn.style.background = 'lightgrey';
          btn.style.position = 'relative';
          btn.innerHTML = text;

          btn.title = tool.tip;
          btn.onmouseover = function() {btn.style.cursor = 'default'};
          btn.onclick = function(e) {
            var grid = this.parentNode.grid;
            if (grid.frame.form.disable_count) return false;
            if (grid.active_row === -1) return false;
            //var args = [grid.ref, grid.active_row];
            var args = [this.ref, grid.active_row];
            send_request('clicked', args);
            grid.focus();
            };

          if (tool.shortcut !== null) {
            var type_key = tool.shortcut.split(',');
            grid.kbd_shortcuts[type_key[0]][type_key[1]] = btn;
          };

          toolbar.appendChild(btn);
          break;
        case 'img':
          var btn = document.createElement('div');
          btn.style[cssFloat] = 'left';
          btn.style.backgroundImage = 'url(images/' + tool.name + '.png)';
          btn.style.width = '16px';
          btn.style.height = '16px';
          btn.style.marginLeft = '5px';
          btn.style.marginRight = '2px';
          btn.style.marginTop = '5px';
          btn.style.position = 'relative';

          frame.form.obj_dict[tool.ref] = btn;
          btn.tabIndex = -1  // remove from tab order
          btn.ref = tool.ref;

          btn.title = tool.tip;
          btn.onclick = function(e) {
            var grid = this.parentNode.grid;
            if (grid.active_row === -1) return false;
            if (grid.frame.form.disable_count) return false;
            //var args = [grid.ref, grid.active_row];
            var args = [this.ref, grid.active_row];
            send_request('clicked', args);
            grid.focus();
            };

          if (tool.shortcut !== null) {
            var type_key = tool.shortcut.split(',');
            grid.kbd_shortcuts[type_key[0]][type_key[1]] = btn;
            };

          toolbar.appendChild(btn);
          break;
        case 'nav':
          // FIRST
          var nav = document.createElement('div');
          nav.style.backgroundImage = 'url(' + iFirst_src + ')';
          nav.style[cssFloat] = 'left';
          nav.style.width = '16px';
          nav.style.height = '16px';
          nav.style.marginLeft = '5px';
          nav.style.marginRight = '2px';
          nav.style.marginTop = '5px';
          nav.style.position = 'relative';
          nav.title = 'Go to top';
          nav.onclick = function(e) {
            var grid = this.parentNode.grid;
            if (grid.frame.form.disable_count) return false;
            grid.goto_top();
            grid.focus();
            };
          toolbar.appendChild(nav);

          // PAGE UP
          var nav = document.createElement('div');
          nav.style.backgroundImage = 'url(' + iPrev_src + ')';
          nav.style[cssFloat] = 'left';
          nav.style.width = '16px';
          nav.style.height = '16px';
          nav.style.marginLeft = '2px';
          nav.style.marginRight = '2px';
          nav.style.marginTop = '5px';
          nav.style.position = 'relative';
          nav.title = 'Page up';
          nav.onclick = function(e) {
            var grid = this.parentNode.grid;
            if (grid.frame.form.disable_count) return false;
            grid.page_up();
            grid.focus();
            }
          toolbar.appendChild(nav);

          // ROW COUNTER
          var row_count = document.createElement('div');
          row_count.style[cssFloat] = 'left';
          row_count.style.marginTop = '5px';
          row_count.style.position = 'relative';
          row_count.innerHTML = '0/0';
          toolbar.appendChild(row_count);
          grid.row_count = row_count;

          // PAGE DOWN
          var nav = document.createElement('div');
          nav.style.backgroundImage = 'url(' + iNext_src + ')';
          nav.style[cssFloat] = 'left';
          nav.style.width = '16px';
          nav.style.height = '16px';
          nav.style.marginLeft = '2px';
          nav.style.marginRight = '2px';
          nav.style.marginTop = '5px';
          nav.style.position = 'relative';
          nav.title = 'Page down';
          nav.onclick = function(e) {
            var grid = this.parentNode.grid;
            if (grid.frame.form.disable_count) return false;
            grid.page_down();
            grid.focus();
            };
          toolbar.appendChild(nav);

          // GO TO BOTTOM
          var nav = document.createElement('div');
          nav.style.backgroundImage = 'url(' + iLast_src + ')';
          nav.style[cssFloat] = 'left';
          nav.style.width = '16px';
          nav.style.height = '16px';
          nav.style.marginLeft = '2px';
          nav.style.marginRight = '5px';
          nav.style.marginTop = '5px';
          nav.style.position = 'relative';
          nav.title = 'Go to bottom';
          nav.onclick = function(e) {
            var grid = this.parentNode.grid;
            if (grid.frame.form.disable_count) return false;
            grid.goto_bottom();
            grid.focus();
            };
          toolbar.appendChild(nav);

          break;
        default: debug3(tool.type + ' UNKNOWN'); break;
        };
      };
    };
  };
