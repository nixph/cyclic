class RawHTTPParser:
    def __init__(self, raw: bytes):
        #print(raw)
        self.ok = True
        self.raw = raw
        self.uri = None
        self.host = None
        self.port = None
        self.body = b''
        self.method = None
        self.headers = {}
        self.protocol_version = None
        try:
            raw, self.body = raw.split(b"\r\n\r\n")
        except Exception as e:
            pass
        raw = raw.split(b"\r\n")
        #print(raw)
        try:
            self.method, self.uri, self.protocol_version = [x.decode() for x in raw[0].split(b" ")]
        except Exception as e:
            self.ok = False
            pass#print(" Error:",e)
        #print(self.method, self.uri, self.protocol_version)
        try:
            self.port = int(self.uri.split(":")[1].split("/")[0])
        except Exception as e:
            pass#print(" Error:",e)
        #print(self.port)
        try:
            self.host = raw[1].split(b'Host: ')[1].decode()
            #print(_host)
        except Exception as e:
            pass#print(" Error:",e)

        try:
            for i in range(2,len(raw)):
                key_value = raw[i].split(b':')
                if len(key_value) == 2:
                    self.headers.update({key_value[0].lower().decode():key_value[1].strip().decode()})
                #print(i)
        except Exception as e:
            pass#print(" Error:",e)
