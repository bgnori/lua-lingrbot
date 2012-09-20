#!/usr/bin/lua
cjson = require 'cjson'
print "Content-Type: text/plain"
print ""
json = cjson.decode(io.read('*all'))
for _, x in ipairs(json.events) do
  _, _, body = string.find(x.message.text, '^!lua (.*)')
  if body and x.message.room == 'computer_science' then
    user = x.message.speaker_id
    fname = user..".env"
    if body == "bot:clear()" then
      os.remove(fname)
      io.write(string.format("***env for %s is cleared.***", user))
    elseif body == "bot:show()" then
      f = io.open(fname, "r")
      body = f:read('*all')
      io.write(body)
      f:close()
    else
      f = io.open(fname, "a+")
      f:write(body.."\r\n")
      f:close()
      f = io.open(fname, "r")
      body = f:read('*all')
      io = {write = io.write}
      os = {date = os.date}
      io.write(loadstring(string.format('return (function () %s end)()', body))())
      f:close()
    end
  end
end
