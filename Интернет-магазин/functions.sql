CREATE OR REPLACE FUNCTION authenticate_user(p_login VARCHAR, p_password VARCHAR)
RETURNS TABLE (id_user INTEGER, roleid INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id_user, u.roleid
    FROM users u
    WHERE u.login = p_login
    AND u.password = p_password;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения ID пользователя по роли
CREATE OR REPLACE FUNCTION get_user_id_by_role(role_name VARCHAR)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT u.Id_user
        FROM Users u
        JOIN Role r ON u.RoleID = r.Id
        WHERE r.Name = role_name
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql;

-- Процедура для создания заказа
CREATE OR REPLACE PROCEDURE create_order(
    p_user_id INTEGER,
    OUT p_order_id INTEGER
) AS $$
BEGIN
    INSERT INTO Orders (Id_user, Date, Status)
    VALUES (p_user_id, CURRENT_DATE, 'В обработке')
    RETURNING Id INTO p_order_id;
END;
$$ LANGUAGE plpgsql;

-- Процедура для добавления товара в заказ
CREATE OR REPLACE PROCEDURE add_order_item(
    p_order_id INTEGER,
    p_product_id INTEGER,
    p_quantity INTEGER
) AS $$
BEGIN
    INSERT INTO Order_items (Id_order, Id_product, Quantity)
    VALUES (p_order_id, p_product_id, p_quantity);

    -- Обновляем количество товара в наличии
    UPDATE Presence
    SET Quantity = Quantity - p_quantity
    WHERE Id_product = p_product_id;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения доступных товаров
CREATE OR REPLACE FUNCTION get_available_products()
RETURNS TABLE (
    id_product INTEGER,
    product_name TEXT,
    category_name VARCHAR,
    price DECIMAL,
    quantity INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.Id_product,
        c.Name || ' ' || p.Id_product::text as product_name,
        c.Name as category_name,
        p.Price,
        pr.Quantity
    FROM Product p
    JOIN Category c ON p.Id_category = c.Id
    JOIN Presence pr ON p.Id_product = pr.Id_product
    WHERE pr.Quantity > 0;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION search_shops(name_pattern TEXT, address_pattern TEXT, login_pattern TEXT)
RETURNS TABLE (
    shop_id INTEGER,
    shop_name VARCHAR,
    shop_address VARCHAR,
    manager_login VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.adress,
        u.login
    FROM shop s
    LEFT JOIN users u ON s.id_user = u.id_user
    WHERE
        LOWER(s.name) LIKE LOWER(name_pattern)
        OR LOWER(s.adress) LIKE LOWER(address_pattern)
        OR LOWER(COALESCE(u.login, '')) LIKE LOWER(login_pattern);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_all_shops()
RETURNS TABLE (
    shop_id INTEGER,
    shop_name VARCHAR,
    shop_address VARCHAR,
    manager_login VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        s.name,
        s.adress,
        COALESCE(u.login, '-') as login  -- если менеджера нет, выводим '-'
    FROM shop s
    LEFT JOIN users u ON s.id_user = u.id_user
    ORDER BY s.id;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION get_managers_list()
RETURNS TABLE (id_user INTEGER, login VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT u.id_user, u.login
    FROM users u
    JOIN role r ON u.roleid = r.id
    WHERE r.name = 'Менеджер магазина'
    ORDER BY u.login;
END;
$$ LANGUAGE plpgsql;





CREATE OR REPLACE FUNCTION get_all_users_with_roles()
RETURNS TABLE (
    user_id INTEGER,
    user_login VARCHAR,
    user_role VARCHAR,
    user_phone VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.Id_user,
        u.Login,
        r.Name AS Role,
        u.Phone
    FROM Users u
    JOIN Role r ON u.RoleID = r.Id
    ORDER BY u.Id_user;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION generate_sales_report_by_user(
    IN p_user_id INTEGER
)
RETURNS TABLE (
    login VARCHAR,
    order_count BIGINT,
    total_amount NUMERIC
) AS $$
DECLARE
    user_role_name VARCHAR;
BEGIN
    -- Получаем роль пользователя
    SELECT r.Name INTO user_role_name
    FROM Users u
    JOIN Role r ON u.RoleID = r.Id
    WHERE u.Id_user = p_user_id;

    -- Если роль администратора или менеджера
    IF user_role_name IN ('Администратор', 'Менеджер магазина') THEN
        RETURN QUERY
        SELECT
            u.login,
            COUNT(DISTINCT o.id)::BIGINT as order_count,
            COALESCE(SUM(p.price * oi.quantity), 0)::NUMERIC as total_amount
        FROM Users u
        LEFT JOIN Orders o ON u.id_user = o.id_user AND o.status = 'Выполнен'
        LEFT JOIN Order_items oi ON o.id = oi.id_order
        LEFT JOIN Product p ON oi.id_product = p.id_product
        GROUP BY u.login
        ORDER BY total_amount DESC;

    -- Для остальных ролей возвращаем пустой результат
    ELSE
        RETURN QUERY
        SELECT NULL::VARCHAR, NULL::BIGINT, NULL::NUMERIC
        WHERE FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Функция для подсчета выполненных заказов
CREATE OR REPLACE FUNCTION count_completed_orders(
    IN p_user_id INTEGER
)
RETURNS INTEGER AS $$
DECLARE
    user_role_name VARCHAR;
    completed_count INTEGER;
BEGIN
    -- Получаем роль пользователя
    SELECT r.Name INTO user_role_name
    FROM Users u
    JOIN Role r ON u.RoleID = r.Id
    WHERE u.Id_user = p_user_id;

    -- Если роль администратора или менеджера
    IF user_role_name IN ('Администратор', 'Менеджер магазина') THEN
        SELECT COUNT(*) INTO completed_count
        FROM Orders
        WHERE status = 'Выполнен';

        RETURN completed_count;

    -- Для остальных ролей возвращаем 0
    ELSE
        RETURN 0;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION generate_inventory_report_by_user(
    IN p_user_id INTEGER
)
RETURNS TABLE (
    category VARCHAR,
    shop VARCHAR,
    product_count BIGINT,
    total_quantity NUMERIC
) AS $$
DECLARE
    user_role_name VARCHAR;
BEGIN
    -- Получаем роль пользователя
    SELECT r.Name INTO user_role_name
    FROM Users u
    JOIN Role r ON u.RoleID = r.Id
    WHERE u.Id_user = p_user_id;

    -- Если роль администратора или менеджера магазина
    IF user_role_name IN ('Администратор', 'Менеджер магазина') THEN
        RETURN QUERY
        SELECT
            c.name AS category,
            s.name AS shop,
            COUNT(p.id_product)::BIGINT AS product_count,
            COALESCE(SUM(pr.quantity), 0)::NUMERIC AS total_quantity
        FROM category c
        JOIN product p ON p.id_category = c.id
        JOIN presence pr ON p.id_product = pr.id_product
        JOIN shop s ON pr.id_shop = s.id
        GROUP BY c.name, s.name
        ORDER BY c.name, s.name;

    -- Если менеджер магазина, показываем только его магазин
    ELSIF user_role_name = 'Менеджер магазина' THEN
        RETURN QUERY
        SELECT
            c.name AS category,
            s.name AS shop,
            COUNT(p.id_product)::BIGINT AS product_count,
            COALESCE(SUM(pr.quantity), 0)::NUMERIC AS total_quantity
        FROM category c
        JOIN product p ON p.id_category = c.id
        JOIN presence pr ON p.id_product = pr.id_product
        JOIN shop s ON pr.id_shop = s.id
        WHERE s.id_user = p_user_id
        GROUP BY c.name, s.name
        ORDER BY c.name, s.name;

    -- Для остальных ролей возвращаем пустой результат
    ELSE
        RETURN QUERY
        SELECT NULL::VARCHAR, NULL::VARCHAR, NULL::BIGINT, NULL::NUMERIC
        WHERE FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION generate_financial_report_by_user(
    IN p_user_id INTEGER
)
RETURNS TABLE (
    total_orders BIGINT,
    total_revenue NUMERIC,
    total_items_sold NUMERIC,
    avg_order_value NUMERIC,
    top_categories TEXT
) AS $$
DECLARE
    user_role_name VARCHAR;
    v_top_categories TEXT;
BEGIN
    -- Получаем роль пользователя
    SELECT r.Name INTO user_role_name
    FROM Users u
    JOIN Role r ON u.RoleID = r.Id
    WHERE u.Id_user = p_user_id;

    -- Если роль администратора или менеджера
    IF user_role_name IN ('Администратор', 'Менеджер магазина') THEN
        -- Вычисляем топ-категории отдельно
        WITH category_sales AS (
            SELECT
                c.name AS category_name,
                COUNT(oi.id) AS sales_count,
                COALESCE(SUM(p.price * oi.quantity), 0) AS category_revenue
            FROM Category c
            LEFT JOIN Product p ON p.id_category = c.id
            LEFT JOIN Order_items oi ON p.id_product = oi.id_product
            LEFT JOIN Orders o ON oi.id_order = o.id
            WHERE o.status = 'Выполнен'
            GROUP BY c.name
            ORDER BY category_revenue DESC
            LIMIT 5
        )
        SELECT
            string_agg(
                category_name || ' | Продаж: ' || sales_count::TEXT ||
                ' | Выручка: ' || category_revenue::TEXT || ' руб.',
                E'\n'
            ) INTO v_top_categories
        FROM category_sales;

        -- Возвращаем финансовые показатели
        RETURN QUERY
        SELECT
            COUNT(DISTINCT o.id)::BIGINT as total_orders,
            COALESCE(SUM(p.price * oi.quantity), 0)::NUMERIC as total_revenue,
            COALESCE(SUM(oi.quantity), 0)::NUMERIC as total_items_sold,
            COALESCE(AVG(p.price * oi.quantity), 0)::NUMERIC as avg_order_value,
            COALESCE(v_top_categories, 'Нет данных')::TEXT as top_categories
        FROM Orders o
        LEFT JOIN Order_items oi ON o.id = oi.id_order
        LEFT JOIN Product p ON oi.id_product = p.id_product
        WHERE o.status = 'Выполнен';

    -- Для остальных ролей возвращаем пустой результат
    ELSE
        RETURN QUERY
        SELECT
            0::BIGINT,
            0::NUMERIC,
            0::NUMERIC,
            0::NUMERIC,
            'Недостаточно прав для просмотра отчета'::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;