package ija.ija2020.homework1.store;

import ija.ija2020.homework1.goods.Goods;
import ija.ija2020.homework1.goods.GoodsItem;

import java.time.LocalDate;

public class StoreGoods implements Goods {

    @Override
    public String getName() {
        return null;
    }

    @Override
    public boolean addItem(GoodsItem goodsItem) {
        return false;
    }

    @Override
    public GoodsItem newItem(LocalDate localDate) {
        return null;
    }

    @Override
    public boolean remove(GoodsItem goodsItem) {
        return false;
    }

    @Override
    public boolean empty() {
        return false;
    }

    @Override
    public int size() {
        return 0;
    }
}
