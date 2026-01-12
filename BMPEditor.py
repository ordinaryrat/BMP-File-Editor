# 1/7/2026, OrdinaryRat

from math import ceil

def splitHexes(hex_string):
    output_list = []
    i = 0;
    while i < len(hex_string):
        # Byte = 2 Hex Characters
        output_list.append(hex_string[i] + hex_string[i + 1]);
        i += 2;
    return output_list;

# This is in order as well
byte_lengths = [
    ["Signature", 2], 
    ["FileSize", 4], 
    ["reserved1", 2], 
    ["reserved2", 2], 
    ["DataOffset", 4], 
    ["Size", 4], 
    ["Width", 4], 
    ["Height", 4], 
    ["Planes", 2], 
    ["Bits Per Pixel", 2], 
    ["Compression", 4], 
    ["ImageSize", 4], 
    ["XpixelsPerM", 4], 
    ["YpixelsPerM", 4], 
    ["Colors Used", 4], 
    ["Important Colors", 4]
];
contents32 = [
    ["bV5RedMask", 4], 
    ["bV5GreenMask", 4], 
    ["bV5BlueMask", 4], 
    ["bV5AlphaMask", 4], 
    ["bV5CSType", 4], 
    ["bV5Endpoints", 36], 
    ["bV5GammaRed", 4], 
    ["bV5GammaGreen", 4], 
    ["bV5GammaBlue", 4], 
    ["bV5Intent", 4], 
    ["bV5ProfileData", 4], 
    ["bV5ProfileSize", 4], 
    ["bV5Reserved", 4],
    ["bV5Reserved2", 12]
];
class Image:
    def __init__(self):
        self.current_parameters = {
            "Signature": 16973, 
            "FileSize": 0, 
            "reserved1": 0, 
            "reserved2": 0, 
            "DataOffset": 54, 
            "Size": 40, 
            "Width": 0, 
            "Height": 0, 
            "Planes": 1, 
            "Bits Per Pixel": -1, 
            "Compression": 0, 
            "ImageSize": 0, 
            "XpixelsPerM": 100, 
            "YpixelsPerM": 100, 
            "Colors Used": 0, 
            "Important Colors": 0,
            "bV5RedMask": 65280, 
            "bV5GreenMask": 16711680, 
            "bV5BlueMask": 4278190080, 
            "bV5AlphaMask": 255, 
            "bV5CSType": 544106839, 
            "bV5Endpoints": 0, 
            "bV5GammaRed": 0, 
            "bV5GammaGreen": 0, 
            "bV5GammaBlue": 0, 
            "bV5Intent": 0, 
            "bV5ProfileData": 0, 
            "bV5ProfileSize": 0, 
            "bV5Reserved": 0,
            "bV5Reserved2": 308276084002010815015158015
        };
        self.scan_lines = []; # Will be a list containing lists of bits (for each pixel)
        
        self.color_table_used = False;
        self.color_table = [];
        self.padding_length = 0;
        
    def loadFromImage(self, image_name):
        file_text = "";
        with open(image_name, "rb") as image_file:
            file_text = image_file.read();
        hex_val = str(file_text.hex());
        current_hex_bytes = splitHexes(hex_val);
        
        # Hex will be decomposed to make it much easier to edit
        current_byte = 0;
        for field in byte_lengths:
            field_hex_val = current_hex_bytes[current_byte:current_byte + field[1]];
            if field[0] != "Signature": # Signature is big-endian rest are little endian
                field_hex_val = field_hex_val[::-1];
            field_int_val = int("".join(field_hex_val), 16);
            field_hex_val = " ".join(field_hex_val);
            field_ascii_val = file_text[current_byte:current_byte + field[1]];
            
            if field[0] == "Bits Per Pixel" and field_int_val == 32:
                byte_lengths.extend(contents32);
                
            self.current_parameters[field[0]] = field_int_val;
            current_byte += field[1];
            
        if self.current_parameters["Bits Per Pixel"] <= 8:
            self.color_table_used = True;
            for color_count in range(self.current_parameters["Colors Used"]):
                field_hex_val = " ".join(current_hex_bytes[current_byte:current_byte + field[1]][::-1]);
                self.color_table.append(field_hex_val);
                current_byte += 4; # Each entry in color table is 4 bytes
                
        scan_line_byte_width = ceil((self.current_parameters["Bits Per Pixel"]/8) * self.current_parameters["Width"]); 
        self.padding_length = int((ceil(scan_line_byte_width / 4) * 4) - scan_line_byte_width);
        
        scan_line_number = 0;
        while scan_line_number < self.current_parameters["Height"]:
            field_hex_val = current_hex_bytes[current_byte:current_byte + scan_line_byte_width];
            self.scan_lines.append([""])
            for hex_byte in field_hex_val:
                current_bits = str(bin(int(hex_byte, 16)));
                current_bits = current_bits[2:];
                current_bits = ('0' * (8 - len(current_bits))) + current_bits; # Padding
                if len(self.scan_lines[-1][-1]) + len(current_bits) <= self.current_parameters["Bits Per Pixel"]:
                    self.scan_lines[-1][-1] += current_bits;
                else:
                    for bit in current_bits:
                        if len(self.scan_lines[-1][-1]) < self.current_parameters["Bits Per Pixel"]:
                            self.scan_lines[-1][-1] += bit;
                        else:
                            self.scan_lines[-1].append(bit);
                
            scan_line_number += 1;
            current_byte += scan_line_byte_width + self.padding_length;
            
        self.scan_lines = self.scan_lines[::-1]; # Will need to flip again at end
        
    def createNewImage(self, width, height, bits_per_pixel, color=(255,255,255,255)):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255);
        if bits_per_pixel == 32:
            self.current_parameters["DataOffset"] = 150;
            self.current_parameters["Size"] = 124;
            self.current_parameters["Compression"] = 3;
            self.current_parameters["XpixelsPerM"] = 50190;
            self.current_parameters["YpixelsPerM"] = 50190;
            color = (color[0], color[3], color[1], color[2]); # Shittiest fix imaginable but it works late at night rather than actually working to fix the bug
        self.current_parameters["FileSize"] = int(self.current_parameters["DataOffset"] + (width * height * bits_per_pixel/8));
        self.current_parameters["Width"] = width;
        self.current_parameters["Height"] = height;
        self.current_parameters["Bits Per Pixel"] = bits_per_pixel;
        
        scan_line_byte_width = ceil((bits_per_pixel/8) * width); 
        self.padding_length = int((ceil(scan_line_byte_width / 4) * 4) - scan_line_byte_width); # Padding done here and is handled when image is written
        if bits_per_pixel <= 8:
            self.color_table_used = True;
            new_hex_value = [hex(color[3])[2:], hex(color[0])[2:], hex(color[1])[2:], hex(color[2])[2:]];
            for i in range(len(new_hex_value)):
                if len(new_hex_value[i]) == 1:
                    new_hex_value[i] = '0' + new_hex_value[i];
            self.color_table.append(" ".join(new_hex_value));
            self.current_parameters["Colors Used"] = 1;
            self.current_parameters["Important Colors"] = 1;
            new_bit_value = bits_per_pixel * '0'
        else: 
            if bits_per_pixel == 24:
                new_bit_value = [bin(color[2])[2:], bin(color[1])[2:], bin(color[0])[2:]];
            else:
                new_bit_value = [bin(color[3])[2:], bin(color[2])[2:], bin(color[1])[2:], bin(color[0])[2:]];
            
            for i in range(len(new_bit_value)):
                if len(new_bit_value[i]) < 8:
                    new_bit_value[i] = ('0' * (8 - len(new_bit_value[i]))) + new_bit_value[i];
            new_bit_value = "".join(new_bit_value);
        for _ in range(height):
            self.scan_lines.append([]);
            for _ in range(width):
                self.scan_lines[-1].append(new_bit_value);
        # print(self.scan_lines);
    # def changeImageSize(self, new_width=-1, new_height=-1, new_color=(255, 255, 255, 255)):
        # pass;
        
    def writePixel(self, position, color):
        #a r g b
        if self.current_parameters["Bits Per Pixel"] == 32:
            color = (color[1], color[3], color[0], color[2]); 
        if position[0] >= self.current_parameters["Width"] or position[1] >= self.current_parameters["Height"]:
            raise Exception("ERROR: Pixel out of bounds");
        if self.color_table_used:
            converted_color_code = [hex(255)[2:] if len(color) == 3 else hex(color[3])[2:], hex(color[0])[2:], hex(color[1])[2:], hex(color[2])[2:]];
            converted_color_code = " ".join(converted_color_code);
            found_value = False;
            for i in range(len(self.color_table)):
                if self.color_table[i] == converted_color_code:
                    found_value = True;
                    break;
            converted_index_value = bin(i);
            if not found_value:
                self.color_table.append(converted_color_code);
                converted_index_value = bin(len(self.color_table) - 1);
                self.current_parameters["Colors Used"] += 1;
                self.current_parameters["Important Colors"] += 1;
            converted_index_value = converted_index_value[2:]
            
            # Technically you should also remove non-existent colors from the color table. Not super important right now.
            if len(converted_index_value) > self.current_parameters["Bits Per Pixel"]:
                raise Exception("ERROR: Attempting to add more colors then the bit count allows");
            if len(converted_index_value) < self.current_parameters["Bits Per Pixel"]:
                converted_index_value = ('0' * (self.current_parameters["Bits Per Pixel"] - len(converted_index_value))) + converted_index_value;
            self.scan_lines[position[1]][position[0]] = converted_index_value;
        else:
            if self.current_parameters["Bits Per Pixel"] == 24:
                converted_color_code = [bin(color[2]), bin(color[1]), bin(color[0])];
            else:
                converted_color_code = [bin(255) if len(color) == 3 else bin(color[3]), bin(color[0]), bin(color[1]), bin(color[2])];
            for i in range(len(converted_color_code)):
                converted_color_code[i] = converted_color_code[i][2:];
                if len(converted_color_code[i]) < 8:
                    converted_color_code[i] = ('0' * (8 - len(str(converted_color_code[i])))) + converted_color_code[i];
            converted_color_code = "".join(converted_color_code);
            self.scan_lines[position[1]][position[0]] = converted_color_code;
            
    def readPixel(self, position):
        if position[0] >= self.current_parameters["Width"] or position[1] >= self.current_parameters["Height"]:
            raise Exception("ERROR: Pixel out of bounds");
        pixel_bit_code = self.scan_lines[position[1]][position[0]];
        if self.color_table_used:
            pixel_colors = self.color_table[int(pixel_bit_code, 2)].split(" ");
            #a r g b
            return (int(pixel_colors[1], 16), int(pixel_colors[2], 16), int(pixel_colors[3], 16), int(pixel_colors[0], 16));
        else:
            if self.current_parameters["Bits Per Pixel"] == 24:
                return (int(pixel_bit_code[16:24], 2), int(pixel_bit_code[8:16], 2), int(pixel_bit_code[0:8], 2), 255);
            else:
                return (int(pixel_bit_code[16:24], 2), int(pixel_bit_code[8:16], 2), int(pixel_bit_code[0:8], 2), int(pixel_bit_code[24:32], 2));
        
    def writeToFile(self, image_name):
        # print(self.current_parameters["bV5RedMask"]);
        # print(self.current_parameters["bV5GreenMask"]);
        # print(self.current_parameters["bV5BlueMask"]);
        # print(self.current_parameters["bV5AlphaMask"]);
        
        # Some values like file size may need to be recalculated
        current_hex_bytes = "";
        new_byte_lengths = byte_lengths;
        if self.current_parameters["Bits Per Pixel"] == 32:
            new_byte_lengths.extend(contents32);
        for parameter in new_byte_lengths:
            current_bit_script = hex(self.current_parameters[parameter[0]])[2:];
            
            if len(current_bit_script) % 2 != 0:
                current_bit_script = '0' + current_bit_script;
                
            if parameter[0] != "Signature":
                current_bit_script = "".join(splitHexes(current_bit_script));
            if len(current_bit_script) < parameter[1] * 2:
                if parameter[0] in ["bV5RedMask", "bV5GreenMask", "bV5BlueMask", "bV5AlphaMask"]:
                    current_bit_script = ('0' * ((parameter[1] * 2) - len(current_bit_script))) + current_bit_script;
                else:
                    current_bit_script += ('0' * ((parameter[1] * 2) - len(current_bit_script)));

            current_hex_bytes += current_bit_script;
            
        if self.color_table_used:
            for color in self.color_table:
                current_color_script = "".join(color.split(" ")[::-1]);
                current_hex_bytes += current_color_script;

        temporary_scan_lines = self.scan_lines[::-1];
        current_byte = ""
        for scan_line in temporary_scan_lines:
            for pixel in scan_line:
                converted_color_code = "";
                if self.color_table_used:
                    current_byte += pixel;
                    if len(current_byte) == 8:
                        current_byte = hex(int(current_byte, 2))[2:];
                        if len(current_byte) == 1:
                            current_byte = '0' + current_byte;
                        current_hex_bytes += current_byte;
                        current_byte = "";
                else:
                    if self.current_parameters["Bits Per Pixel"] == 24:
                        converted_color_code = [hex(int(pixel[16:24], 2)), hex(int(pixel[8:16], 2)), hex(int(pixel[0:8], 2))][::-1];
                    else:
                        # converted_color_code = [hex(int(pixel[24:32], 2)), hex(int(pixel[0:8], 2)), hex(int(pixel[16:24], 2)), hex(int(pixel[8:16], 2))];
                        converted_color_code = [hex(int(pixel[0:8], 2)), hex(int(pixel[8:16], 2)), hex(int(pixel[24:32], 2)), hex(int(pixel[16:24], 2))];
                    for i in range(len(converted_color_code)):
                        converted_color_code[i] = converted_color_code[i][2:];
                        if len(converted_color_code[i]) == 1:
                            converted_color_code[i] = '0' + converted_color_code[i];
                    converted_color_code = "".join(converted_color_code);
                    # print(converted_color_code);
                current_hex_bytes += converted_color_code;
            if len(current_byte) > 0:
                #neccessarily less than 8 though
                current_byte = ('0' * (8 - len(current_byte))) + current_byte;
                current_byte = hex(int(current_byte, 2))[2:];
                if len(current_byte) == 1:
                    current_byte = '0' + current_byte;
                current_hex_bytes += current_byte;
                current_byte = "";
            for _ in range(self.padding_length):
                current_hex_bytes += "00";
        output_bytes = bytes.fromhex(current_hex_bytes);
        with open(image_name, "wb") as image_output:

            image_output.write(output_bytes);

