#!/usr/bin/lua


function sandbox (chunk, buf)
  -- http://lua-users.org/wiki/SandBoxes
  local env = {
      next = next; 
      pairs = pairs;
      print = print;
      io = {
          write = io.write;
          stdout = buf
      };
      os = {date = os.date};
      debug = {};
      _G = {}
  }
  compiled = loadstring(string.format('return (function () %s end)()', chunk))
  setfenv(compiled, env)
  return pcall(compiled)
end

function Response ()
    local obj = {}
    obj.body = io.tmpfile()
    obj.headers = {}

    function obj.render(self, ofile)
      assert(self)
      assert(self.render)
      assert(self.body)
      assert(self.headers)
      if type(self.headers["Content-Length"]) == 'nil' then
        len = self.body:seek('end')
        self.headers["Content-Length"] = string.format('%d', len)
      end
      for h, v in pairs(self.headers) do
        hds = string.format("%s: %s\r\n", h, v)
        assert(hds)
        ofile:write(hds)
      end
      ofile:write("\r\n")
      self.body:seek('set')
      ofile:write(self.body:read('*all'))
    end

    assert(obj.render)
    assert(obj.body)
    assert(obj.headers)

    return obj
end



cjson = require 'cjson'
json = cjson.decode(io.read('*all'))

r = Response()
r.headers["Content-Type"] = "text/plain"
assert(r.body)
assert(r.render)
assert(r.headers)
for k, v in pairs(r.headers) do
    print(k)
end

for _, x in ipairs(json.events) do
  _, _, body = string.find(x.message.text, '^!lua (.*)')
  if body and x.message.room == 'computer_science' then
    user = x.message.speaker_id
    fname = user..".env"
    if body == "bot:clear()" then
      os.remove(fname)
      r.body:write(string.format("***env for %s is cleared.***", user))
    elseif body == "bot:show()" then
      f = io.open(fname, "r")
      body = f:read('*all')
      r.body:write(body)
      f:close()
    else
      f = io.open(fname, "a+")
      f:write(body.."\r\n")
      f:close()
      f = io.open(fname, "r")
      body = f:read('*all')
      buf = io.tmpfile()
      result = sandbox(body, buf)
      if type(result) == "nil" then
        buf:write("nil")
      else
        buf:write(tostring(result))
      end
      buf:seek('set')
      r.body:write(buf:read())
      f:close()
    end
  end
end
r:render(io.stdout)

