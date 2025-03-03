-- Триггер для проверки количества товара перед добавлением в заказ
CREATE OR REPLACE FUNCTION check_quantity_before_order()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    available_quantity INTEGER;
BEGIN
    -- Получаем доступное количество товара
    SELECT Quantity INTO available_quantity
    FROM Presence
    WHERE Id_product = NEW.Id_product;

    -- Проверяем достаточно ли товара
    IF available_quantity IS NULL OR available_quantity < NEW.Quantity THEN
        RAISE EXCEPTION 'Недостаточное количество товара (доступно: %, требуется: %)', 
            COALESCE(available_quantity, 0), NEW.Quantity;
    END IF;
    
    RETURN NEW;
END;
$$;

CREATE TRIGGER check_quantity_trigger
BEFORE INSERT ON Order_items
FOR EACH ROW
EXECUTE FUNCTION check_quantity_before_order();

-- Триггер для обновления количества товара после создания заказа
CREATE OR REPLACE FUNCTION update_presence_after_order()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Обновляем количество товара после добавления в заказ
    UPDATE Presence
    SET Quantity = Quantity - NEW.Quantity
    WHERE Id_product = NEW.Id_product;
    
    -- Проверяем, что количество не стало отрицательным
    IF EXISTS (
        SELECT 1 
        FROM Presence 
        WHERE Id_product = NEW.Id_product 
        AND Quantity < 0
    ) THEN
        RAISE EXCEPTION 'Ошибка: отрицательное количество товара после обновления';
    END IF;
    
    RETURN NEW;
END;
$$;

CREATE TRIGGER update_presence_trigger
AFTER INSERT ON Order_items
FOR EACH ROW
EXECUTE FUNCTION update_presence_after_order();
