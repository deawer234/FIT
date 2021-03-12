- cpu.vhd: Simple 8-bit CPU (BrainFuck interpreter)
-- Copyright (C) 2013 Brno University of Technology,
--                    Faculty of Information Technology
-- Author(s): Zdenek Vasicek <vasicek AT fit.vutbr.cz>
--

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

-- ----------------------------------------------------------------------------
--                        Entity declaration
-- ----------------------------------------------------------------------------
entity cpu is
 port (
   CLK   : in std_logic;  -- hodinovy signal
   RESET : in std_logic;  -- asynchronni reset procesoru
   EN    : in std_logic;  -- povoleni cinnosti procesoru
 
   -- synchronni pamet ROM
   CODE_ADDR : out std_logic_vector(11 downto 0); -- adresa do pameti
   CODE_DATA : in std_logic_vector(7 downto 0);   -- CODE_DATA <- rom[CODE_ADDR] pokud CODE_EN='1'
   CODE_EN   : out std_logic;                     -- povoleni cinnosti
   
   -- synchronni pamet RAM
   DATA_ADDR  : out std_logic_vector(9 downto 0); -- adresa do pameti
   DATA_WDATA : out std_logic_vector(7 downto 0); -- mem[DATA_ADDR] <- DATA_WDATA pokud DATA_EN='1'
   DATA_RDATA : in std_logic_vector(7 downto 0);  -- DATA_RDATA <- ram[DATA_ADDR] pokud DATA_EN='1'
   DATA_RDWR  : out std_logic;                    -- cteni (1) / zapis (0)
   DATA_EN    : out std_logic;                    -- povoleni cinnosti
   
   -- vstupni port
   IN_DATA   : in std_logic_vector(7 downto 0);   -- IN_DATA <- stav klavesnice pokud IN_VLD='1' a IN_REQ='1'
   IN_VLD    : in std_logic;                      -- data platna
   IN_REQ    : out std_logic;                     -- pozadavek na vstup data
   
   -- vystupni port
   OUT_DATA : out  std_logic_vector(7 downto 0);  -- zapisovana data
   OUT_BUSY : in std_logic;                       -- LCD je zaneprazdnen (1), nelze zapisovat
   OUT_WE   : out std_logic                       -- LCD <- OUT_DATA pokud OUT_WE='1' a OUT_BUSY='0'
 );
end cpu;


-- ----------------------------------------------------------------------------
--                      Architecture declaration
-- ----------------------------------------------------------------------------
architecture behavioral of cpu is

signal pc_code_addr : std_logic_vector(11 downto 0);
signal pc_inc : std_logic;
signal pc_dec : std_logic;
signal pc_ld : std_logic;

signal ptr_data_addr : std_logic_vector(9 downto 0);
signal ptr_inc : std_logic;
signal ptr_dec : std_logic;

signal cnt_data : std_logic_vector(7 downto 0);
signal cnt_inc : std_logic;
signal cnt_dec : std_logic;
signal cnt_data_one : std_logic;

signal cnt_data_null : std_logic;

signal ras_data: std_logic_vector(191 downto 0);
signal ras_push: std_logic;
signal ras_pop: std_logic;

signal sel : std_logic_vector(1 downto 0);
signal data_rdata_null : std_logic;


type fsm_state is (INIT, sfetsh0, sdecode, INC_PTR, DEC_PTR,
		INC_DATA1, INC_DATA2, DEC_DATA1, DEC_DATA2, DATA_LCD1, DATA_LCD2, DATA_LCD3, DATA_LCD4,
		READ_DATA1, READ_DATA2, WHILE_START1, WHILE_START2, WHILE_START3, WHILE_START4, WHILE_START5, WHILE_START6,
		WHILE_END1, WHILE_RAS_PUSH, WHILE_END2, WHILE_RAS_POP, WHILE_END_LOAD, 
		SNULL, OSTATNI);
		
signal pstate : fsm_state;
signal nstate : fsm_state;


begin

--PC programovy citac, ukazuje do pameti ROM (pamet programu)
--ctou se instrukce
pc: process (RESET, CLK, pc_ld)
begin
	if (RESET = '1') then
		pc_code_addr <= (others => '0'); --dostani se do puvodniho stavu, ukazuji na bunku 0
	elsif (CLK'event) and (CLK = '1') then 
		if (pc_inc = '1') then
			pc_code_addr <= pc_code_addr + 1; --inc
		elsif (pc_dec = '1') then
			pc_code_addr <= pc_code_addr - 1; --dec
		elsif (pc_ld = '1') then
			pc_code_addr <= ras_data(191 downto 180);
		end if;
	end if;
end process pc;

CODE_ADDR <= pc_code_addr;

--PTR programovy citac, ukazuje do pameti RAM (datova pamet)

ptr: process (RESET, CLK)
begin
	if (RESET = '1') then
		ptr_data_addr <= (others => '0'); --dostani se do puvodniho stavu, ukazuji na bunku 0
	elsif (CLK'event) and (CLK = '1') then 
		if (ptr_inc = '1') then
			ptr_data_addr <= ptr_data_addr + 1; --inc
		elsif (ptr_dec = '1') then
			ptr_data_addr <= ptr_data_addr- 1; --dec
		end if;
	end if;
end process ptr;

DATA_ADDR <= ptr_data_addr;

--MUX, co se ma zapisovat do pameti RAM
DATA_WDATA <= IN_DATA when (sel = "00") else
				  (DATA_RDATA + 1) when (sel = "01") else
				  (DATA_RDATA - 1) when (sel = "10") else
				  (others => '0');
				  
data_rdata_null <= '1' when (DATA_RDATA = "00000000") else '0';

--CNT smycky 
cnt: process (RESET, CLK, cnt_data_one)
begin
	if (RESET = '1') then
		cnt_data <= (others => '0');
	elsif (CLK'event) and (CLK = '1') then 
		if (cnt_inc = '1') then
			cnt_data <= cnt_data + 1; --inc
		elsif (cnt_dec = '1') then
			cnt_data <= cnt_data - 1; --dec
	elsif (cnt_data_one = '1') then
			cnt_data <= "00000001";
		end if;
	end if;
end process cnt;

cnt_data_null <= '1' when (cnt_data = "00000000") else '0';

--posuvny registr RAS
ras: process(RESET, CLK)
begin
	if (RESET = '1') then
		ras_data <= (others => '0');
	elsif (CLK'event) and (CLK = '1') then
		if (ras_push = '1') then
			ras_data <= pc_code_addr & ras_data(191 downto 12);
		elsif (ras_pop = '1') then
			ras_data <= ras_data(179 downto 0) & "000000000000";       
		end if;
	end if;
end process ras;
			


--FSM, ridi cely procesor
fsm_pstate: process (RESET, CLK)
	begin
		if (RESET = '1') then
			pstate <= INIT;
		elsif (CLK'event) and (CLK = '1') then
			if (EN = '1') then
				pstate <= nstate;
			end if;
		end if;
end process fsm_pstate;
	
fsm_nstate: process (pstate,data_rdata_null, cnt_data_null, EN, CODE_DATA, DATA_RDATA, IN_VLD, IN_DATA, OUT_BUSY)
	begin
		pc_inc <= '0';	--pro PC
		pc_dec <= '0';
		pc_ld <= '0';
		
		ptr_inc <= '0'; --pro PTR
		ptr_dec <= '0';
		
		cnt_inc <= '0';
		cnt_dec <= '0';
		
		ras_push <= '0';
		ras_pop <= '0';
		
		sel <= "11"; 	--pro MUX
		
		CODE_EN <= '0'; --pro ROM
		
		DATA_RDWR <= '0'; --pro RAM
		DATA_EN <= '0'; 
		
		OUT_WE <= '0'; -- pro I/O
		IN_REQ <= '0';
		
		case pstate is
		--IDLE
			when INIT =>
				nstate <= sfetsh0;
				
		--nacteni instrukce do CODE_DATA, povoleni CODE_EN
			when sfetsh0 =>
				nstate <= sdecode;
				CODE_EN <= '1';
			
		--dekodovani instrukci, neboli co dalsiho se delat
			when sdecode =>
				case CODE_DATA is
					when X"3E" =>
						nstate <= INC_PTR; --inkrementace ukazatele na RAM
					when X"3C" =>
						nstate <= DEC_PTR; --dektrementace ukazatele na RAM
					when X"2B" =>
						nstate <= INC_DATA1; --inkrementace aktualni bunky v RAM
					when X"2D" =>
						nstate <= DEC_DATA1; --dekrementace aktualni bunky v RAM
					when X"2E" =>
						nstate <= DATA_LCD1; --tisk dat na LCD display
					when X"2C" =>
						nstate <= READ_DATA1; --cteni z klavesnice
					when X"5B" =>
						nstate <= WHILE_START1; --zacatek cyklu
					when X"5D" =>
						nstate <= WHILE_END1; --konec cyklus
					when X"00" =>
						nstate <= SNULL; --stop
					when others =>
						nstate <= OSTATNI; --kdyz je kod jiny
				end case;
				
-- > incrementace citace PTR, incrementace hodnoty ukazatele				
			when INC_PTR =>
				nstate <= sfetsh0;
				ptr_inc <= '1';
				pc_inc <= '1';
				
-- < decrementace citace PTR, decrementace hodnoty ukazatele				
			when DEC_PTR =>
				nstate <= sfetsh0;
				ptr_dec <= '1';
				pc_inc <= '1';
				
-- + incrementace hodnoty aktualni bunky 			
			when INC_DATA1 =>
				nstate <= INC_DATA2;
				DATA_EN <= '1';
				DATA_RDWR <= '1'; --data z pameti do DATA_RDATA
				
-- + pokracovani incrementace aktualni bunky				
			when INC_DATA2 =>
				nstate <= sfetsh0;
				sel <= "01";
				DATA_EN <= '1';
				DATA_RDWR <= '0'; --data do RAM
				pc_inc <= '1';
				
-- - decrementace hodnoty aktualni bunky 				
			when DEC_DATA1 =>
				nstate <= DEC_DATA2;
				DATA_EN <= '1';
				DATA_RDWR <= '1';
				
-- - pokracovani decrementace aktualni bunky				
			when DEC_DATA2 =>
				nstate <= sfetsh0;
				sel <= "10";
				DATA_EN <= '1';
				DATA_RDWR <= '0';
				pc_inc <= '1';
				
-- . tisknuti hodnoty aktualni bunky na LCD cast 1.				
			when DATA_LCD1 =>
				if (OUT_BUSY = '1') then
					nstate <=DATA_LCD1;
				else
					nstate <= DATA_LCD2;
					DATA_EN <= '1';
					DATA_RDWR <= '1';
				end if;
				
-- . tisknuti hodnoty aktualni bunky na LCD cast 2.				
			when DATA_LCD2 =>
				nstate <= DATA_LCD3;
				DATA_EN <= '1';
				DATA_RDWR <= '1';

			when DATA_LCD3 =>
				nstate <= DATA_LCD4;
				OUT_DATA <= DATA_RDATA;
				
			when DATA_LCD4 =>
				OUT_WE <= '1';
				pc_inc <= '1';
				nstate <= sfetsh0;
			
-- , hodnota z klavesnice se ulozi do aktualni bunky cast 1.				
			when READ_DATA1 =>
				IN_REQ <= '1';
				if (IN_VLD /= '1') then
					nstate <= READ_DATA1;
				else
					nstate <= READ_DATA2;
				end if;
				
-- , hodnota z klavesnice se ulozi do aktualni bunky cast 2.				
			when READ_DATA2 =>
				nstate <= sfetsh0;
				sel <= "00";
				DATA_EN <= '1';
				DATA_RDWR <= '0';
				pc_inc <= '1';
				
-- [ cyklus START!
			when WHILE_START1 =>
				nstate <= WHILE_START2;
				pc_inc <= '1';
				DATA_EN <= '1';
				DATA_RDWR <= '1';
				
-- pokracovani cyklu, zjisteni zda aktualni bunka RAM je nulova
			when WHILE_START2 =>
				if (data_rdata_null = '1') then
					nstate <= WHILE_START3;
				else
					nstate <= WHILE_RAS_PUSH;
				end if;
				
--ukoncovani cyklu pri nespneni podminky, push na RAS
			when WHILE_RAS_PUSH =>
				nstate <= sfetsh0;
				ras_push <= '1';

				
-- pokracovani cyklu, zapsani 1 do cnt
			when WHILE_START3 =>
				nstate <= WHILE_START4;
				cnt_data_one <= '1';
				
-- podminka  cyklu
			when WHILE_START4 =>
				if (cnt_data_null = '0') then
					nstate <= WHILE_START5;
				else
					nstate <= sfetsh0;
				end if;

-- cteni z mapeti ROM
			when WHILE_START5 =>
				nstate <= WHILE_START6;
				CODE_EN <= '1';
				
-- increment nebo decrement citace CNT
			when WHILE_START6 =>
				nstate <= WHILE_START4;
				if (CODE_DATA = X"5B") then
					cnt_inc <= '1';
				elsif (CODE_DATA = X"5D") then
					cnt_dec <= '1';
				end if;
				pc_inc <= '1';
				
-- cyklus END
			when WHILE_END1 =>
				nstate <= WHILE_END2;
				DATA_EN <= '1';
				DATA_RDWR <= '1';
				
-- cyklus END porovanani zda je bunka 0
			when WHILE_END2 =>
				if (data_rdata_null = '1') then
					nstate <= WHILE_RAS_POP;
				else
					nstate <= WHILE_END_LOAD;
				end if;
					
--cyklus END RAS POP
			when WHILE_RAS_POP =>
				nstate <= sfetsh0;
				pc_inc <= '1';
				ras_pop <= '1';
				
--cyklus END lload
			when WHILE_END_LOAD =>
				nstate <= sfetsh0;
				pc_ld <= '1';
				
			
				
			when SNULL =>
				nstate <= SNULL;
				
			when OSTATNI =>
				nstate <= sfetsh0;
				pc_inc <= '1';
				
			when others =>
				null;
		end case;
	end process;
end behavioral;
