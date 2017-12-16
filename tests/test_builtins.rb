# TESTS for the py2rb/builtins/module.rb module

$LOAD_PATH.unshift(File.join(File.dirname(__FILE__), '..'))
require 'test/unit'
require 'module'

class PyBultinsTest < Test::Unit::TestCase
  using PythonZipEx
  def test_zip_p
    vals = [[[[0]],               [0]],
            [[[0,5]],             [0],    [5]],
            [[[0,5],[1,6]],       [0,1],  [5,6]],
            [[[0,5],[1,6],[2,7]], [0,1,2],[5,6,7]],
            [[[0,5,8],[1,6,9]],   [0,1],  [5,6], [8,9]]]
    vals.each{|expect, base, second, third|
      if !third.nil?
        ret = zip_p(base, second, third)
      elsif !second.nil?
        ret = zip_p(base, second)
      else
        ret = zip_p(base)
      end
      assert_equal expect, ret, "base:#{base}, second:#{second}"
    }
  end

  using PythonIsBoolEx
  def test_is_bool_true
    vals = [1, true, -1, 'a', [1], {a: 1}]
    vals.each{|val|
      ret = is_bool(val)
      assert_equal true, ret, val
    }
  end

  def test_is_bool_false
    vals = [nil, false, 0, [], '', {}]
    vals.each{|val|
      ret = is_bool(val)
      assert_equal false, ret, val
    }
  end

  # Python
  #   str.find(sub[, start])
  # Ruby
  #   str.index(sub[, start])
  using PythonIndexEx
  def test_index
       # result, str,       sub,  start
    vals = [[0,  'aiueo',   'ai',   0],
            [0,  'aiueoai', 'ai',   nil],
            [1,  'aiueo',   'iu',   nil],
            [-1, 'aiueo',   'iu',   2],
            [1,  'aiueo',   'iu',   1],
            [-1, 'aiueo',   'hoge', nil]]
    vals.each{|expect, str, substr, start_pos|
      if !start_pos.nil?
        ret = str.index(substr, start_pos)
      else
        ret = str.index(substr)
      end
      assert_equal expect, ret, "str:#{str} substr:#{substr} start_pos:#{start_pos}"
    }
  end

  # Python
  #   str.find(sub[, start[, end]])
  # Ruby
  #   str.find(sub[, start[, end]])
  using PythonIndexEx
  def test_find
       # result, str,       sub,  start, end
    vals = [[0,  'aiueo',   'ai',   0,   nil],
            [0,  'aiueoai', 'ai',   nil, nil],
            [1,  'aiueo',   'iu',   nil, nil],
            [-1, 'aiueo',   'iu',   2,   nil],
            [1,  'aiueo',   'iu',   1,   3],
            [-1, 'aiueo',   'iu',   1,   2],
            [-1, 'aiueo',   'hoge', nil, nil]]
    vals.each{|expect, str, substr, start_pos, end_pos|
      if !end_pos.nil?
        ret = str.find(substr, start_pos, end_pos)
      elsif !start_pos.nil?
        ret = str.find(substr, start_pos)
      else
        ret = str.find(substr)
      end
      assert_equal expect, ret, "str:#{str} substr:#{substr} start_pos:#{start_pos} end_pos:#{end_pos}"
    }
  end

  # Python
  #   str.rindex(sub)
  # Ruby
  #   str.rindex(sub)
  def test_rindex
       # result, str,       sub
    vals = [[0,  'aiueo',   'ai'],
            [5,  'aiueoai', 'ai'],
            [1,  'aiueo',   'iu'],
            [-1, 'aiueo',   'hoge']]
    vals.each{|expect, str, substr|
      ret = str.rindex(substr)
      assert_equal expect, ret, "str:#{str} substr:#{substr}"
    }
  end

  # Python
  #   str.rfind(sub[, start[, end]])
  # Ruby
  #   str.rfind(sub[, start[, end]])
  def test_rfind
       # result, str,       sub,  start, end
    vals = [[0,  'aiueo',   'ai',   0,   nil],
            [5,  'aiueoai', 'ai',   nil, nil],
            [1,  'aiueo',   'iu',   nil, nil],
            [-1, 'aiueo',   'iu',   2,   nil],
            [1,  'aiueo',   'iu',   1,   3],
            [-1, 'aiueo',   'iu',   1,   2],
            [1,  'aiueo',   'iu',   1,   -1],
            [-1, 'aiueo',   'hoge', nil, nil]]
    vals.each{|expect, str, substr, start_pos, end_pos|
      if !end_pos.nil?
        ret = str.rfind(substr, start_pos, end_pos)
      elsif !start_pos.nil?
        ret = str.rfind(substr, start_pos)
      else
        ret = str.rfind(substr)
      end
      assert_equal expect, ret, "str:#{str} substr:#{substr} start_pos:#{start_pos} end_pos:#{end_pos}"
    }
  end
end
