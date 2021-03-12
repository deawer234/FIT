-- cpu.vhd: Simple 8-bit CPU (BrainF*ck interpreter)
-- Copyright (C) 2020 Brno University of Technology,
--                    Faculty of Information Technology
-- Author(s): DOPLNIT
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
   DATA_WDATA : out std_logic_vector(7 downto 0); -- ram[DATA_ADDR] <- DATA_WDATA pokud DATA_EN='1'
   DATA_RDATA : in std_logic_vector(7 downto 0);  -- DATA_RDATA <- ram[DATA_ADDR] pokud DATA_EN='1'
   DATA_WE    : out std_logic;                    -- cteni (0) / zapis (1)
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

 -- zde dopiste potrebne deklarace signalu
 -- PC
	signal pc_reg : std_logic_vector(11 downto 0);
	signal pc_inc : std_logic;
	signal pc_dec : std_logic;
	signal pc_ld  : std_logic;
 -- PTR
	signal ptr_reg : std_logic_vector(9 downto 0);
	signal ptr_inc : std_logic;
	signal ptr_dec : std_logic;
 -- CNT
	signal cnt_reg : std_logic_vector(7 downto 0);
	signal cnt_inc : std_logic;
	signal cnt_dec : std_logic;
	signal cnt_set_one : std_logic;
	signal cnt_data : std_logic;

 -- RAS
	signal ras_reg: std_logic_vector(191 downto 0);
	signal ras_push: std_logic;
	signal ras_pop: std_logic;
	
 -- STATES
	type fsm_state is (
	       state_start,
	       state_fetch,
	       state_decode,

	       state_pointer_inc,
	       state_pointer_dec,
			 

	       state_value_inc,
	       state_value_inc_mx,
	       	       state_value_inc_end,
	       state_value_dec,
	       state_value_dec_mx,
	        state_value_dec_end,

	       state_while_start,
			 state_while_1,
			 state_while_2,
			 state_while_3,
			 state_while_4,
			 state_while_set,
	       state_while_end,
			 state_while_end_1,
			  state_while_load,

	       state_write,
			 state_write_end,
			 state_write_out,
			 state_write_out_end,
			 
	       state_read,
			 state_read_end,

	       state_push,
	       state_pop,
			 
	       state_null);
	 signal state : fsm_state;
	 signal next_state : fsm_state;
 -- MUX 
	 signal mx_select : std_logic_vector (1 downto 0) := (others => '0');
	 signal data_rdata_null : std_logic;
	 

begin

 -- zde dopiste vlastni VHDL kod


 -- pri tvorbe kodu reflektujte rady ze cviceni INP, zejmena mejte na pameti, ze 
 --   - nelze z vice procesu ovladat stejny signal,
 --   - je vhodne mit jeden proces pro popis jedne hardwarove komponenty, protoze pak
 --   - u synchronnich komponent obsahuje sensitivity list pouze CLK a RESET a 
 --   - u kombinacnich komponent obsahuje sensitivity list vsechny ctene signaly.

 --- PC
	reg_pc: process (RESET, CLK, pc_ld, pc_dec, pc_inc) is
	begin
		if (RESET='1') then
			pc_reg <= (others=>'0');
		elsif (CLK'event) and (CLK='1') then
			if (pc_inc='1') then
				pc_reg <= pc_reg + 1;
			elsif (pc_dec = '1') then
				pc_reg <= pc_reg - 1;
			elsif (pc_ld = '1') then
				pc_reg <= ras_reg(191 downto 180); 	
			end if;
		end if;
	end process reg_pc;
	
	CODE_ADDR <= pc_reg;

 --- PTR

	reg_ptr: process (RESET, CLK, ptr_inc, ptr_dec) is
	begin
		if (RESET='1') then
			ptr_reg <= (others=>'0');
		elsif (CLK'event) and (CLK='1') then
			if (ptr_inc='1') then
				ptr_reg <= ptr_reg + 1;
			elsif (ptr_dec = '1') then
				ptr_reg <= ptr_reg - 1;
			end if;
		end if;
	end process reg_ptr;
	
	DATA_ADDR <= ptr_reg;
	

 --- CNT
	cnt: process(RESET, CLK, cnt_set_one, cnt_inc, cnt_dec)
	begin 
		if(RESET = '1') then
			cnt_reg <= (others=>'0');
		elsif (CLK'event and CLK = '1') then
			if(cnt_inc = '1') then
				cnt_reg <= cnt_reg + 1;
			elsif(cnt_dec = '1') then
				cnt_reg <= cnt_reg - 1;
		elsif (cnt_set_one = '1') then
				cnt_reg <= "00000001";
			end if;
		end if;	

	end process cnt;

	--cnt_data <= '1' when (cnt_reg = "00000000") else '0';

 --- MUX

	mux: process (CLK, RESET, mx_select) is
	begin
		if (RESET = '1') then
			DATA_WDATA <= (others => '0');
		elsif (CLK'event) and (CLK='1') then
			case mx_select is
				when "00" =>
				DATA_WDATA <= IN_DATA;
			when "01" =>
				DATA_WDATA <= DATA_RDATA + 1;
			when "10" =>
				DATA_WDATA <= DATA_RDATA - 1;
			when others =>
				DATA_WDATA <= (others => '0');
		end case;
	end if;	
	end process;

	--DATA_WDATA <= IN_DATA when (mx_select = "00") else
	--			  (DATA_RDATA + 1) when (mx_select = "01") else
	--			  (DATA_RDATA - 1) when (mx_select = "10") else
	--			  (others => '0');
	
	data_rdata_null <= '1' when (DATA_RDATA = "00000000") else '0';

	
 --- RAS

	ras: process(RESET, CLK, ras_push, ras_pop)
	begin
		if (RESET = '1') then
			ras_reg <= (others => '0');
		elsif (CLK'event) and (CLK = '1') then
			if (ras_push = '1') then
				ras_reg <= pc_reg & ras_reg(191 downto 12);
			elsif (ras_pop = '1') then
				ras_reg <= ras_reg(179 downto 0) & "000000000000";       
			end if;
		end if;
	end process;



 --- FSM MEALY
	
	state_logic: process (CLK, RESET, EN) is
	begin 
		if (RESET = '1') then
			state <= state_start;
		elsif (CLK'event) and (CLK='1') then
			if (EN = '1') then
				state <= next_state;
			end if;
		end if;
	end process;
	
	fsm: process (state, OUT_BUSY, IN_VLD, CODE_DATA, DATA_RDATA, IN_DATA, OUT_BUSY, data_rdata, cnt_reg) is
	begin 
		pc_inc <= '0';
		pc_dec <= '0';
		pc_ld <= '0';

		ras_pop <= '0';
		ras_push <= '0';

		ptr_inc <= '0';
		ptr_dec <= '0';
		
		cnt_dec <= '0';
		cnt_inc <= '0';

		CODE_EN <= '0';
		DATA_EN <= '0';
		DATA_WE <= '0';
		IN_REQ <= '0';
		OUT_WE <= '0';

		mx_select <= "11";

		case state is
			when state_start =>
				next_state <= state_fetch;
			when state_fetch =>
				CODE_EN <= '1';
				next_state <= state_decode;
			when state_decode =>
				case CODE_DATA is
					when X"3E" => next_state <= state_pointer_inc; -- >
					when X"3C" => next_state <= state_pointer_dec; -- <
					when X"2B" => next_state <= state_value_inc; -- +
					when X"2D" => next_state <= state_value_dec; -- -
					when X"5B" => next_state <= state_while_start; -- [
					when X"5D" => next_state <= state_while_end; -- ]
					when X"2E" => next_state <= state_write; -- .
					when X"2C" => next_state <= state_read; -- ,
					when X"00" => next_state <= state_null;
					when others =>
						pc_inc <= '1';
						next_state <= state_fetch;
				end case;
			when state_pointer_inc =>
				ptr_inc <= '1';
				pc_inc <= '1';
				next_state <= state_fetch;
				
			when state_pointer_dec =>
				ptr_dec <= '1';
				pc_inc <= '1';
				next_state <= state_fetch;
				
			when state_value_inc =>
				DATA_WE <= '0';
				DATA_EN <= '1';
				next_state <= state_value_inc_mx;
				
			when state_value_inc_mx =>
				mx_select <= "01";
				next_state <= state_value_inc_end;

			when state_value_inc_end =>
				DATA_EN <= '1';
				DATA_WE <= '1';
				pc_inc <= '1';
				next_state <= state_fetch;			
				
			when state_value_dec =>
				DATA_WE <= '0';
				DATA_EN <= '1';
				next_state <= state_value_dec_mx;
				
			when state_value_dec_mx =>
				mx_select <= "10";
				next_state <= state_value_dec_end;

			when state_value_dec_end =>
				DATA_EN <= '1';
				DATA_WE <= '1';
				pc_inc <= '1';
				next_state <= state_fetch;

							
			when state_write =>
				if (OUT_BUSY = '1') then
					next_state <= state_write;
				else
					DATA_EN <= '1';
					DATA_WE <= '0';
					next_state <= state_write_end;
				end if;
			
			when state_write_end =>
				DATA_EN <= '1';
				DATA_WE <= '0';
				next_state <= state_write_out;
					
			when state_write_out =>
				OUT_DATA <= DATA_RDATA;
				next_state <= state_write_out_end;
			
			when state_write_out_end =>
				OUT_WE <= '1';
				pc_inc <= '1';
				next_state <= state_fetch;
				
			when state_read =>
				IN_REQ <= '1';
				if (IN_VLD /= '1') then
					next_state <= state_read;
				else
					next_state <= state_read_end;
				end if;
			
			when state_read_end =>
				mx_select <= "00";
				DATA_EN <= '1';
				DATA_WE <= '1';
				pc_inc <= '1';
				next_state <= state_fetch;
				
			when state_while_start =>
				pc_inc <= '1';
				DATA_EN <= '1';
				DATA_WE <= '0';	
				next_state <= state_while_1;
				
			when state_while_1 =>
				if (DATA_RDATA = "00000000") then
					next_state <= state_while_set;
				else
					next_state <= state_push;
				end if;

			when state_while_set =>
				cnt_set_one <= '1';	
				next_state <= state_while_2;
				
			when state_while_2 =>
				if(cnt_reg = "00000000") then
					next_state <= state_fetch;
				else 
					next_state <= state_while_3;
				end if;
				
			when state_while_3 =>
				CODE_EN <= '1';
				next_state <= state_while_4;
				
			when state_while_4 =>
				if (CODE_DATA = X"5B") then
					cnt_inc <= '1';
				elsif (CODE_DATA = X"5D") then
					cnt_dec <= '1';
				end if;
				pc_inc <= '1';
				next_state <= state_while_2;
				
			when state_while_end =>
				DATA_EN <= '1';
				DATA_WE <= '0';
				next_state <= state_while_end_1;
			
			when state_while_end_1 =>
				if (DATA_RDATA = "00000000") then
					next_state <= state_pop;
				else	
					next_state <= state_while_load;
				end if;

			when state_while_load =>
				pc_ld <= '1';	
				next_state <= state_fetch;

			when state_pop =>
				pc_inc <= '1';
				ras_pop <= '1';
				next_state <= state_fetch;

			when state_push =>
				ras_push <= '1';
				next_state <= state_fetch;

			when state_null =>
				next_state <= state_null;

			when others =>
				null;
			
	
		end case;
	end process;
end behavioral;
 

 
