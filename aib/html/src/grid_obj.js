function create_cell_input(grid) {

  var input = document.createElement('input');
  input.className = 'focus_background';
  input.style.border = 'none';
  input.style.outline = '0px solid transparent';  // disable highlight on focus
  input.style.height = '17px';
  input.style.padding = '1px';
  input.style.font = '10pt Verdana,sans-serif';
  input.style.color = 'navy';
  input.grid = grid;

  input.get_val = function() {
    return this.value;
    };

  input.get_caret = function() {
    return getCaret(this);
    };

  input.set_value_from_server = function(args) {
    if (this.grid.active_row === -1)  // grid not yet set up
      return
    var row = args[0], value = args[1];
    input.aib_obj.set_cell_value_from_server(this.grid, row, this.col, value);
    };

  input.reset_value = function() {
    if (this.grid.active_row === -1)  // grid not yet set up
      return
    var grid = this.grid;
    var cell = grid.grid_rows[grid.active_row-grid.first_grid_row].grid_cols[this.col];
    input.aib_obj.reset_cell_value(cell);
    };

  input.edit_cell = function(cell, current_value, keyCode) {
    input.style.width = cell.style.width;
    this.cell = cell;  // save for use in end_edit()
    cell.style.display = 'none';
    cell.parentNode.appendChild(input);

    this.grid.save_onkeypress = this.grid.onkeypress;
    this.grid.save_onkeydown = this.grid.onkeydown;
    this.grid.onkeypress = null;
    this.grid.onkeydown = null;

    if (keyCode === null) {
      if (current_value === null)
        current_value = cell.text_node.data;
//      if (current_value === '\xa0')
//        current_value = '';
      };

    grid.edit_in_progress = true;
    input.aib_obj.start_edit(input, current_value, keyCode);
    input.className = cell.className;
    input.focus();
//    debug3(input.offsetHeight + ' ' + input.parentNode + ' ' + input.parentNode.offsetHeight);
    };

  input.end_edit = function(update, reset_focus) {
    var cell = this.cell, grid = this.grid;
    grid.edit_in_progress = false;
    if (update) {
      if (!input.aib_obj.before_cell_lost_focus(input))  // validation failed
        return false;
      // before_lost_focus() copies input.value to input.current_value
      cell.current_value = input.current_value;
      cell.text_node.data = input.value;
      grid.row_amended = true;
      if (grid.grid_frame !== null)
        grid.grid_frame.frame_amended = true;
      };
    cell.parentNode.removeChild(input);
    cell.style.display = 'inline-block';
    grid.onkeypress = grid.save_onkeypress;
    grid.onkeydown = grid.save_onkeydown;
    if (reset_focus) {
      this_grid = grid;  // make global
      setTimeout(function() {this_grid.focus()}, 0);  // IE needs timeout!
      };
    return true;
    }

  input.onkeypress = function(e) {
    if (!e) e=window.event;
    return input.aib_obj.onpresskey(input, e);
    };

  input.onkeydown = function(e) {
    if (!e) e=window.event;
    switch (e.keyCode) {
      case 9:  // tab
        if (input.end_edit(true, true))
          this.grid.handle_tab(e.shiftKey);
        e.cancelBubble = true;
        return false;
        break;
      case 13:  // enter
        // either 'end edit *and* move down' or just 'end edit'
        // for now, run with the second option
        // slight problem [2013-12-31]
        // if we just 'end edit', nothing is sent to the server, so the entry
        //   is not validated, and the db_obj is not updated (same as F2 - see below)
        // could change things to treat it like a check-box click, so that it
        //   is validated in-situ
        // for now, run with the first option
        // this is treated on the server as 'save changes and move down' without
        //   asking for confirmation, same as making changes and 'tabbing' to
        //   the next row
        if (input.end_edit(true, true))  // first option
          this.grid.handle_enter();
        //input.end_edit(true, true);  // second option
        e.cancelBubble = true;
        return false;
        break;
      case 27:  // escape
        input.end_edit(false, true);
        e.cancelBubble = true;
        return false;
        break;
      case 113:  // F2
        input.end_edit(true, true);
        e.cancelBubble = true;
        return false;
        break;
      default:
        return input.aib_obj.ondownkey(input, e);
        break;
      };
    };

  input.handle_backslash = function() {
    if (this.grid.active_row > 0) {
      var prev_value = this.grid.subset_data[
        this.grid.first_subset_row + this.grid.active_row - 1][this.grid.active_col];
      var cell = this.grid.get_active_cell();
      input.edit_cell(
        cell, cell.aib_obj.convert_prev_cell_value(cell, prev_value), null);
      };
    };

  return input;
  };

function create_grid_cell(col_span, col_defn, first, last) {

  //var cell = document.createElement('span');
  //cell.style.display = 'inline-block';
  var cell = document.createElement('div');
  cell.style[cssFloat] = 'left';
//  cell.style.border = ' 2px solid transparent';
  cell.style.width = col_defn.lng + 'px';
  cell.style.height = '17px';
  col_span.cell = cell;
  col_span.appendChild(cell);

  cell.onmouseover = function() {cell.style.cursor = 'default'};
  cell.onmouseleave = function() {cell.style.cursor = 'default'};

  if (col_defn.type === 'bool') {
    cell.style.textAlign = 'center';

    var chkbox = document.createElement('span');
    chkbox.style.display = 'inline-block';
    chkbox.style.width = '16px';
    chkbox.style.height = '16px';
    chkbox.style.border = '1px solid darkgrey';

    cell.appendChild(chkbox);
    cell.chkbox = chkbox;

    if (window.SVGSVGElement !== undefined) {  // else use vml
      var NS='http://www.w3.org/2000/svg';
      var svg=document.createElementNS(NS,'svg');
      chkbox.appendChild(svg);
      };

    cell.highlight = function(state) {
      switch (state) {
        case 'clear':
          cell.firstChild.style.border = '1px solid darkgrey';
          cell.firstChild.className = 'blur_background';
          break;
        case 'error':
          var border = '1px solid black';
          cell.firstChild.className = 'error_background';
          break;
        case 'readonly':
          var border = '1px solid black';
          cell.firstChild.className = 'readonly_background';
          break;
        case 'blur':
          var border = '1px solid black';
          cell.firstChild.className = 'blur_background';
          break;
        case 'focus':
          var border = '1px solid black';
          cell.firstChild.className = 'focus_background';
          break;
        };
      };

    chkbox.onclick = function(e) {
      if (!e) e=window.event;
      var cell = chkbox.parentNode;
      var grid = cell.grid;
      if (grid.frame.form.disable_count) return false;
      var this_row = grid.first_grid_row + cell.grid_row, this_col = cell.grid_col;
      if (this_row !== grid.active_row || this_col !== grid.active_col) {
        callbacks.push([chkbox, chkbox.afterclick, cell, this_row]);
        grid.req_cell_focus(this_row, this_col, false);
        }
      else
        cell.aib_obj.grid_chkbox_change(cell, this_row);
      e.cancelBubble = true;
      return false;  // prevent bubble up to cell.onclick()
      };
    chkbox.afterclick = function(cell, this_row) {
      //if (cell.grid.focus_from_server)  // server has set focus somewhere else
      if (cell.grid.get_active_cell() !== cell)  // server has set focus somewhere else
        return;
      cell.aib_obj.grid_chkbox_change(cell, this_row)
      };
    }

  else if (col_defn.type === 'sxml') {
    cell.style.textAlign = 'center';

    var sxml = document.createElement('span');
    sxml.style.display = 'inline-block';
    sxml.style.width = '60px';
    sxml.style.height = '16px';
    sxml.style.border = '1px solid darkgrey';
    sxml.appendChild(document.createTextNode('<xml>'));

    cell.appendChild(sxml);
    cell.sxml = sxml;

    cell.highlight = function(state) {
      switch (state) {
        case 'clear':
          cell.firstChild.style.border = '1px solid darkgrey';
          cell.firstChild.className = 'blur_background';
          break;
        case 'error':
          var border = '1px solid black';
          cell.firstChild.className = 'error_background';
          break;
        case 'readonly':
          var border = '1px solid black';
          cell.firstChild.className = 'readonly_background';
          break;
        case 'blur':
          var border = '1px solid black';
          cell.firstChild.className = 'blur_background';
          break;
        case 'focus':
          var border = '1px solid black';
          cell.firstChild.className = 'focus_background';
          break;
        };
      };

    sxml.onclick = function(e) {
      if (!e) e=window.event;
      var cell = sxml.parentNode;
      var grid = cell.grid;
      if (grid.frame.form.disable_count) return false;
      var this_row = grid.first_grid_row + cell.grid_row, this_col = cell.grid_col;
      if (this_row !== grid.active_row || this_col !== grid.active_col) {
        callbacks.push([sxml, sxml.afterclick, cell, this_row]);
        grid.req_cell_focus(this_row, this_col, false);
        }
      else
        sxml.afterclick(cell, this_row);
      e.cancelBubble = true;
      return false;  // prevent bubble up to cell.onclick()
      };
    sxml.afterclick = function(cell, this_row) {
      //if (cell.grid.focus_from_server)  // server has set focus somewhere else
      if (cell.grid.get_active_cell() !== cell)  // server has set focus somewhere else
        return;
      cell.aib_obj.grid_popup(cell, this_row);
      };
    }

  else {
    cell.style.overflow = 'hidden';
    cell.style.textOverflow = 'ellipsis';
    cell.style.whiteSpace = 'nowrap';

    var txt = document.createElement('span');
    cell.appendChild(txt);
    txt.style.whiteSpace = 'pre';
    txt.style.display = 'inline-block';
    txt.style.height = '17px';
    txt.style.background = '#F5F5F5';  // very light grey

    cell.highlight = function(state) {
      switch (state) {
        case 'clear':
          var border = '1px solid darkgrey';
          cell.className = 'blur_background';
          cell.firstChild.style.background = '#F5F5F5';
          break;
        case 'error':
          var border = '1px solid black';
          cell.className = 'error_background';
          cell.firstChild.style.background = 'mistyrose';
          break;
        case 'readonly':
          var border = '1px solid black';
          cell.className = 'readonly_background';
          cell.firstChild.style.background = '#B4EEB4';
          break;
        case 'blur':
          var border = '1px solid black';
          cell.className = 'blur_background';
          cell.firstChild.style.background = '#F5F5F5';
          break;
        case 'focus':
          var border = '1px solid black';
          cell.className = 'focus_background';
          cell.firstChild.style.background = '#C0FFFF';
          break;
        };

/*
      if (state === true) {
        var border = '1px solid black';
        if (grid.err_flag) {
          cell.className = 'error_background';
          cell.firstChild.style.background = 'mistyrose';
          }
        else if (cell.input.readonly || !cell.input.allow_amend) {
          cell.className = 'readonly_background';
          cell.firstChild.style.background = '#CCFFCC';  //'#A9F5A9';
          }
        else {
          cell.className = 'focus_background';
          cell.firstChild.style.background = '#c0ffff';
          };
        }
      else {
        var border = '1px solid darkgrey';
        cell.className = 'blur_background';
        cell.firstChild.style.background = '#f5f5f5';
        };
*/

      var col_span = cell.parentNode;
      var grid = cell.grid;
      col_span.style.borderBottom = border;
      col_span.style.borderRight = border;
      if (cell.grid_row)
        grid.childNodes[((cell.grid_row-1)*2)+2]
          .childNodes[cell.grid_col].style.borderBottom = border;
      if (cell.grid_col)
        grid.childNodes[(cell.grid_row*2)+2]
          .childNodes[(cell.grid_col-1)].style.borderRight = border;
      else
        col_span.style.borderLeft = border;
      };
    };

  var btn = null;

  switch (col_defn.type) {
    case 'text':
      cell.text_node = document.createTextNode('');  //('\xa0');

      if (col_defn.lkup) {

        // create 2-part button - top: req_lookup  bottom: req_lookdown
        //var btn = document.createElement('span');
        //btn.style.display = 'inline-block';
        var btn = document.createElement('div');
        btn.style[cssFloat] = 'right';
        col_span.appendChild(btn);
        btn.style.backgroundImage = 'url(' + iLkup_src + ')';
        btn.style.width = '16px';
        btn.style.height = '16px';
//        btn.style.margin = '2px 2px 2px 0px';  // top/right/bottom/left
        btn.style.margin = '1px 1px 0px 1px';  // top/right/bottom/left
        btn.onmouseover = function() {
          btn.style.cursor = 'pointer';
          };
        btn.onmouseleave = function() {
          btn.style.cursor = 'default';
          };

        var lkup = document.createElement('div');
        btn.appendChild(lkup);
        lkup.style.width = '15px';
        lkup.style.height = '7px';
        lkup.style.background = 'transparent';
        lkup.title = 'Call lookup (Space)';

        lkup.onclick = function() {
          var cell = this.parentNode.parentNode.firstChild;
          var grid = cell.grid;
          if (grid.frame.form.disable_count) return false;
          callbacks.push([lkup, lkup.afterclick, cell]);
          grid.req_cell_focus((grid.first_grid_row + cell.grid_row), cell.grid_col, false);
          };

        lkup.afterclick = function() {
          //if (cell.grid.focus_from_server)  // server has set focus somewhere else
          if (cell.grid.get_active_cell() !== cell)  // server has set focus somewhere else
            return;
          cell.input.expander();
          };

        var blank = document.createElement('div');
        btn.appendChild(blank);
        blank.style.width = '15px';
        blank.style.height = '1px';
        blank.style.background = 'transparent';

        var lkdn = document.createElement('div');
        btn.appendChild(lkdn);
        lkdn.style.width = '15px';
        lkdn.style.height = '7px';
        lkdn.style.background = 'transparent';
        lkdn.title = 'Call lookdown (Shift+Enter)';
        lkdn.onclick = function(e) {
          var cell = this.parentNode.parentNode.firstChild;
          var grid = cell.grid;
          if (grid.frame.form.disable_count) return false;
          callbacks.push([lkdn, lkdn.afterclick, cell]);
          grid.req_cell_focus((grid.first_grid_row + cell.grid_row), cell.grid_col, false);
          };
        lkdn.afterclick = function() {
          //if (cell.grid.focus_from_server)  // server has set focus somewhere else
          if (cell.grid.get_active_cell() !== cell)  // server has set focus somewhere else
            return;
          cell.input.lookdown();
          };

        };

      txt.appendChild(cell.text_node);
      break;
    case 'num':
      cell.text_node = document.createTextNode('');  //('\xa0');
      txt.appendChild(cell.text_node);
      cell.style.textAlign = 'right';
      break;
    case 'date':
      cell.text_node = document.createTextNode('');  //('\xa0');
      txt.appendChild(cell.text_node);

      //var btn = document.createElement('span');
      //btn.style.display = 'inline-block';
      var btn = document.createElement('div');
      btn.style[cssFloat] = 'right';
      col_span.appendChild(btn);
      btn.style.backgroundImage = 'url(' + iCal_src + ')';
      btn.style.width = '16px';
      btn.style.height = '16px';
//      btn.style.margin = '2px 2px 2px 0px';  // top/right/bottom/left
      btn.style.margin = '1px 1px 0px 1px';  // top/right/bottom/left
      btn.title = 'Calendar (Space)';

      btn.onmouseover = function() {
        this.style.cursor = 'pointer';
        };
      btn.onmouseleave = function() {
        this.style.cursor = 'default';
        };
      btn.onclick = function() {
        var cell = this.parentNode.firstChild;
        var grid = cell.grid;
        if (grid.frame.form.disable_count) return false;
        callbacks.push([btn, btn.afterclick, cell]);
        grid.req_cell_focus((grid.first_grid_row + cell.grid_row), cell.grid_col, false);
        };
      btn.afterclick = function(cell) {
        //debug3('after click ' + cell.grid_row + ' ' + cell.grid_col
        //  + ' ' + cell.grid.focus_from_server);
        //if (cell.grid.focus_from_server)  // server has set focus somewhere else
        if (cell.grid.get_active_cell() !== cell)  // server has set focus somewhere else
          return;
        date = cell.input
        date.cell = cell;
        cell.aib_obj.grid_show_cal(date)
        };

      break;
    case 'choice':
      cell.text_node = document.createTextNode('');  //('\xa0');
      txt.appendChild(cell.text_node);

      //var btn = document.createElement('span');
      //btn.style.display = 'inline-block';
      var btn = document.createElement('div');
      btn.style[cssFloat] = 'right';
      col_span.appendChild(btn);
      btn.style.backgroundImage = 'url(' + iDown_src + ')';
      //btn.style.width = '16px';
      //btn.style.height = '16px';
      //btn.style.margin = '1px 1px 0px 1px';  // top/right/bottom/left
      btn.style.width = '17px';
      btn.style.height = '17px';
//      btn.style.paddingRight = '1px';
//      btn.style.borderTop = '1px solid transparent';
//      btn.style.borderBottom = '1px solid transparent';
      btn.title = 'Show choices (Space)';

      btn.onmouseover = function(e) {
        this.style.cursor = 'pointer';
        };
      btn.onmouseleave = function(e) {
        this.style.cursor = 'default';
        };
      btn.onclick = function(e) {
        if (!e) e=window.event;
        var cell = this.parentNode.parentNode.firstChild;
        var grid = cell.grid;
        if (grid.frame.form.disable_count) return false;
        callbacks.push([btn, btn.afterclick, cell]);
        grid.req_cell_focus((grid.first_grid_row + cell.grid_row), cell.grid_col, false);
        };
      btn.afterclick = function(cell) {
        //debug3('after click ' + cell.grid_row + ' ' + cell.grid_col
        //  + ' ' + cell.grid.focus_from_server);
        //if (cell.grid.focus_from_server)  // server has set focus somewhere else
        if (cell.grid.get_active_cell() !== cell)  // server has set focus somewhere else
          return;
        cell.aib_obj.grid_create_dropdown(cell);
        };

      break;
    };

    if (btn !== null) {
      cell.btn = btn;
      cell.style.borderTop = '1px solid transparent';
      cell.style.borderBottom = '1px solid transparent';
      btn.style.borderTop = '1px solid transparent';
      btn.style.borderBottom = '1px solid transparent';
      if (first)
        cell.style.borderLeft = '1px solid transparent';
      else
        cell.style.paddingLeft = '1px';
      btn.style.paddingLeft = '1px';
      if (last)
        btn.style.borderRight = '1px solid transparent';
      else
        btn.style.paddingRight = '1px';

      if (first && last)
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.btn.style.borderTop = border;
          cell.btn.style.borderBottom = border;
          cell.style.borderLeft = border;
          cell.btn.style.borderRight = border;
          };
      else if (first)
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.btn.style.borderTop = border;
          cell.btn.style.borderBottom = border;
          cell.style.borderLeft = border;
          };
      else if (last)
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.btn.style.borderTop = border;
          cell.btn.style.borderBottom = border;
          cell.btn.style.borderRight = border;
          };
      else
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.btn.style.borderTop = border;
          cell.btn.style.borderBottom = border;
          };
      }

    else {
      cell.style.borderTop = '1px solid transparent';
      cell.style.borderBottom = '1px solid transparent';
      if (first)
        cell.style.borderLeft = '1px solid transparent';
      else
        cell.style.paddingLeft = '1px';
      if (last)
        cell.style.borderRight = '1px solid transparent';
      else
        cell.style.paddingRight = '1px';

      if (first && last)
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.style.borderLeft = border;
          cell.style.borderRight = border;
          };
      else if (first)
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.style.borderLeft = border;
          };
      else if (last)
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          cell.style.borderRight = border;
          };
      else
        cell.set_row_highlight = function(border) {
          cell.style.borderTop = border;
          cell.style.borderBottom = border;
          };

      };

  return cell;
  };
