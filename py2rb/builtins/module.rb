# frozen_string_literal: true
module PythonZipEx
  refine Object do
    # python : zip(l1, l2, [l3, ..])
    #  array : l1
    def zip_p(*args)
      args.collect!{|i| i.is_a?(String) ? i.split(''): i}
      a = args.shift
      return a.zip(*args).select{|i| !i.include?(nil)}
    end
  end
end

module PythonMethodEx
  refine Object do
    def getattr(*a)
      if singleton_class.class_variables.include? "@@#{a[0]}".to_sym
        send(a[0])
      elsif public_methods.include? a[0].to_sym
        method(a[0])
      elsif a.size == 2
        return a[1]
      else
        raise NoMethodError, "undefined method `#{a[0]}'"
      end
    end
  end
end

module PythonPrintEx
  refine Object do
    def print(*args)
      $, = ' ';$\ = "\n"
      super(*args)
    end
  end
end

module PythonIsBoolEx
  refine Object do
    def is_bool(a)
      case a
      when nil, false, 0, '', [], {}
        return false
      else
        return true
      end
    end
  end
end

module PythonIndexEx
  refine String do
    def index(substr, offset=0)
      ret = super(substr, offset)
      return ret.nil? ? -1 : ret
    end

    def rindex(substr)
      ret = super(substr)
      return ret.nil? ? -1 : ret
    end
  end
end

module PythonFindEx
  refine String do
    def find(substr, start_pos=0, end_pos=nil)
      if end_pos.nil?
        ret = index(substr, start_pos)
      else
        ret = self[0...end_pos].public_method(:index).call(substr, start_pos)
      end
      return ret.nil? ? -1 : ret
    end

    def rfind(substr, start_pos=0, end_pos=nil)
      if end_pos.nil?
        ret = self[start_pos..-1].public_method(:rindex).call(substr)
        unless ret.nil?
          ret = self[0..-1].public_method(:rindex).call(substr)
        end
      else
        ret = self[start_pos...end_pos].public_method(:rindex).call(substr)
        unless ret.nil?
          ret = self[0...end_pos].public_method(:rindex).call(substr)
        end
      end
      return ret.nil? ? -1 : ret
    end
  end
end

module PythonSplitEx
  refine String do
    def split_p(sep = '', limit=0)
      case sep
      when ' '
        sep = / /
      when ''
        sep = $;
      end
      if limit > 0
        limit +=1
      end
      self.split(sep, limit)
    end
  end
end

module PythonStripEx
  refine String do
    def strip(chars='')
      if chars == ''
         super()
      else
         self.gsub(/(^[#{chars}]*)|([#{chars}]*$)/, '')
      end
    end

    def lstrip(chars='')
      if chars == ''
         super()
      else
         self.gsub(/(^[#{chars}]*)/, '')
      end
    end

    def rstrip(chars='')
      if chars == ''
         super()
      else
         self.gsub(/([#{chars}]*$)/, '')
      end
    end
  end
end

module PythonStringCountEx
  refine String do
    # Replace to Python String#count
    alias :count_r :count
    def count(substr, start_pos=nil, end_pos=nil)
      if start_pos.nil?
         self.scan(substr).size
      elsif end_pos.nil?
         self[start_pos..-1].scan(substr).size
      else
         self[start_pos...end_pos].scan(substr).size
      end
    end

    alias :each :chars
  end
end

module PythonRemoveEx
  refine Array do
    def remove(obj)
      i = self.index(obj)
      self.delete_at(i)
      return
    end
  end
end

module EnumerableEx
  refine Enumerable do
    def is_all?()
      result = true
      self.each do |a|
        case a
        when nil, false, 0, '', [], {}
          result =  false
        end
      end
      return result
    end

    def is_any?()
      result = false
      self.each do |a|
        case a
        when nil, false, 0, '', [], {}
        else
          result =  true
        end
      end
      return result
    end
  end
end

module PyLib
  require 'pathname'

# tests/os/testdir/
#              test_file1.txt
#              test_file2.txt
#              test_child_dir/
#                  test_child_file1.txt
#                  test_child_file2.txt
#<dirpath>  tests/os/testdir
#<dirnames> ['test_child_dir']
#<filenames>['test_file1.txt', 'test_file2.txt']
#
#<dirpath>  tests/os/testdir/test_child_dir
#<dirnames> []
#<filenames>['test_child_file1.txt', 'test_child_file2.txt']

#<dirpath> tests/os/testdir
#<dirnames> ["tests/os/testdir/test_child_dir"]
#<filenames> ["tests/os/testdir/test_child_dir/test_child_file1.txt", "tests/os/testdir/test_child_dir/test_child_file2.txt", "tests/os/testdir/test_file1.txt", "tests/os/testdir/test_file2.txt"]

  def self.walk(dir)
    dirpath = Pathname(dir)
    rootnames = []
    Pathname(dirpath).find do |path|
      if path.directory?
        rootnames << path.to_s
      end
    end

    walks = []
    rootnames.each{|root|
      dirnames = []
      filenames = []
      
      Dir.foreach(root){|f|
        path = File.join(root, f)
        case File.ftype(path)
        when 'directory'
          if ('.' != f) and ('..' != f)
            dirnames << f
          end
        when 'file'
          filenames << f
        end
      }
      walks << [root, dirnames, filenames]
    }

    return walks
  end
end

#
# Foo.call() or Foo.() is nothing => Foo.new() call.
#
class Class
  def method_missing(method, *args)
    if method == :call
      self.new(*args)
    else
      super
    end
  end
end

require 'set'
class Set
  def remove(x)
    self.delete(x)
    return
  end
end
